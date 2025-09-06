/**
 * General API Routes
 * Example endpoints for hackathon projects with security and validation
 */

const express = require('express');
const { body, query, validationResult } = require('express-validator');
const router = express.Router();

const { authorize, requirePermission } = require('../middleware/auth');
const { catchAsync, AppError } = require('../middleware/errorHandler');
const logger = require('../utils/logger');

// In-memory data store for examples (replace with database)
const projects = new Map();
const tasks = new Map();

// Validation rules
const projectValidation = [
  body('name')
    .trim()
    .isLength({ min: 3, max: 100 })
    .withMessage('Project name must be between 3 and 100 characters'),
  body('description')
    .optional()
    .trim()
    .isLength({ max: 500 })
    .withMessage('Description must not exceed 500 characters'),
  body('category')
    .isIn(['web', 'mobile', 'ai', 'blockchain', 'iot', 'fintech', 'healthtech', 'edutech'])
    .withMessage('Invalid project category'),
  body('tags')
    .optional()
    .isArray()
    .withMessage('Tags must be an array'),
  body('tags.*')
    .optional()
    .trim()
    .isLength({ min: 1, max: 20 })
    .withMessage('Each tag must be between 1 and 20 characters')
];

const taskValidation = [
  body('title')
    .trim()
    .isLength({ min: 3, max: 100 })
    .withMessage('Task title must be between 3 and 100 characters'),
  body('description')
    .optional()
    .trim()
    .isLength({ max: 1000 })
    .withMessage('Description must not exceed 1000 characters'),
  body('priority')
    .isIn(['low', 'medium', 'high', 'critical'])
    .withMessage('Priority must be low, medium, high, or critical'),
  body('status')
    .optional()
    .isIn(['todo', 'in_progress', 'review', 'done'])
    .withMessage('Status must be todo, in_progress, review, or done'),
  body('projectId')
    .notEmpty()
    .withMessage('Project ID is required'),
  body('dueDate')
    .optional()
    .isISO8601()
    .withMessage('Due date must be a valid ISO 8601 date')
];

/**
 * @route   GET /api/v1/projects
 * @desc    Get all projects with filtering and pagination
 * @access  Private
 */
router.get('/projects', requirePermission('read'), catchAsync(async (req, res) => {
  const {
    page = 1,
    limit = 10,
    category,
    search = '',
    sortBy = 'createdAt',
    sortOrder = 'desc'
  } = req.query;
  
  // Convert projects Map to array
  let projectList = Array.from(projects.entries()).map(([id, project]) => ({
    id,
    ...project
  }));
  
  // Filter by category
  if (category) {
    projectList = projectList.filter(project => project.category === category);
  }
  
  // Filter by search term
  if (search) {
    const searchLower = search.toLowerCase();
    projectList = projectList.filter(project =>
      project.name.toLowerCase().includes(searchLower) ||
      project.description?.toLowerCase().includes(searchLower) ||
      project.tags?.some(tag => tag.toLowerCase().includes(searchLower))
    );
  }
  
  // Filter by user's projects (non-admin users only see their own)
  if (req.user.role !== 'admin') {
    projectList = projectList.filter(project => project.createdBy === req.user.id);
  }
  
  // Apply sorting
  projectList.sort((a, b) => {
    let aValue = a[sortBy];
    let bValue = b[sortBy];
    
    if (sortBy === 'createdAt' || sortBy === 'updatedAt') {
      aValue = new Date(aValue);
      bValue = new Date(bValue);
    }
    
    if (sortOrder === 'asc') {
      return aValue > bValue ? 1 : -1;
    } else {
      return aValue < bValue ? 1 : -1;
    }
  });
  
  // Apply pagination
  const startIndex = (page - 1) * limit;
  const endIndex = startIndex + parseInt(limit);
  const paginatedProjects = projectList.slice(startIndex, endIndex);
  
  // Calculate pagination info
  const totalProjects = projectList.length;
  const totalPages = Math.ceil(totalProjects / limit);
  
  res.json({
    success: true,
    data: {
      projects: paginatedProjects,
      pagination: {
        currentPage: parseInt(page),
        totalPages,
        totalProjects,
        hasNextPage: endIndex < totalProjects,
        hasPrevPage: startIndex > 0,
        limit: parseInt(limit)
      }
    }
  });
}));

/**
 * @route   POST /api/v1/projects
 * @desc    Create a new project
 * @access  Private
 */
router.post('/projects', requirePermission('write'), projectValidation, catchAsync(async (req, res) => {
  // Check validation results
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({
      success: false,
      error: 'Validation failed',
      details: errors.array()
    });
  }
  
  const { name, description, category, tags = [] } = req.body;
  
  // Check if project name already exists for this user
  const existingProject = Array.from(projects.values()).find(
    project => project.name.toLowerCase() === name.toLowerCase() && 
               project.createdBy === req.user.id
  );
  
  if (existingProject) {
    return res.status(409).json({
      success: false,
      error: 'Project already exists',
      message: 'A project with this name already exists'
    });
  }
  
  const projectId = `project_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  const newProject = {
    name,
    description,
    category,
    tags,
    status: 'active',
    createdBy: req.user.id,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    team: [req.user.id], // Creator is automatically part of the team
    settings: {
      isPublic: false,
      allowCollaboration: true
    }
  };
  
  projects.set(projectId, newProject);
  
  // Log project creation
  logger.audit('project_created', 'project', projectId, {
    name,
    category,
    createdBy: req.user.id
  });
  
  res.status(201).json({
    success: true,
    message: 'Project created successfully',
    data: {
      project: {
        id: projectId,
        ...newProject
      }
    }
  });
}));

/**
 * @route   GET /api/v1/projects/:id
 * @desc    Get project by ID
 * @access  Private
 */
router.get('/projects/:id', requirePermission('read'), catchAsync(async (req, res) => {
  const { id } = req.params;
  const project = projects.get(id);
  
  if (!project) {
    throw new AppError('Project not found', 404);
  }
  
  // Check if user has access to this project
  if (req.user.role !== 'admin' && 
      project.createdBy !== req.user.id && 
      !project.team.includes(req.user.id)) {
    throw new AppError('Access denied to this project', 403);
  }
  
  // Get associated tasks
  const projectTasks = Array.from(tasks.entries())
    .filter(([_, task]) => task.projectId === id)
    .map(([taskId, task]) => ({ id: taskId, ...task }));
  
  res.json({
    success: true,
    data: {
      project: {
        id,
        ...project,
        tasks: projectTasks
      }
    }
  });
}));

/**
 * @route   PUT /api/v1/projects/:id
 * @desc    Update project
 * @access  Private (project owner or admin)
 */
router.put('/projects/:id', requirePermission('write'), projectValidation, catchAsync(async (req, res) => {
  const { id } = req.params;
  const project = projects.get(id);
  
  if (!project) {
    throw new AppError('Project not found', 404);
  }
  
  // Check ownership or admin privileges
  if (req.user.role !== 'admin' && project.createdBy !== req.user.id) {
    throw new AppError('Only project owner or admin can update this project', 403);
  }
  
  // Check validation results
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({
      success: false,
      error: 'Validation failed',
      details: errors.array()
    });
  }
  
  const { name, description, category, tags } = req.body;
  
  const updatedProject = {
    ...project,
    ...(name && { name }),
    ...(description && { description }),
    ...(category && { category }),
    ...(tags && { tags }),
    updatedAt: new Date().toISOString()
  };
  
  projects.set(id, updatedProject);
  
  // Log project update
  logger.audit('project_updated', 'project', id, {
    updatedBy: req.user.id,
    changes: { name, description, category, tags }
  });
  
  res.json({
    success: true,
    message: 'Project updated successfully',
    data: {
      project: {
        id,
        ...updatedProject
      }
    }
  });
}));

/**
 * @route   DELETE /api/v1/projects/:id
 * @desc    Delete project
 * @access  Private (project owner or admin)
 */
router.delete('/projects/:id', requirePermission('delete'), catchAsync(async (req, res) => {
  const { id } = req.params;
  const project = projects.get(id);
  
  if (!project) {
    throw new AppError('Project not found', 404);
  }
  
  // Check ownership or admin privileges
  if (req.user.role !== 'admin' && project.createdBy !== req.user.id) {
    throw new AppError('Only project owner or admin can delete this project', 403);
  }
  
  // Delete associated tasks
  const projectTaskIds = Array.from(tasks.entries())
    .filter(([_, task]) => task.projectId === id)
    .map(([taskId, _]) => taskId);
  
  projectTaskIds.forEach(taskId => tasks.delete(taskId));
  
  // Delete project
  projects.delete(id);
  
  // Log project deletion
  logger.audit('project_deleted', 'project', id, {
    deletedBy: req.user.id,
    projectName: project.name,
    deletedTasks: projectTaskIds.length
  });
  
  res.json({
    success: true,
    message: 'Project and associated tasks deleted successfully'
  });
}));

/**
 * @route   POST /api/v1/tasks
 * @desc    Create a new task
 * @access  Private
 */
router.post('/tasks', requirePermission('write'), taskValidation, catchAsync(async (req, res) => {
  // Check validation results
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({
      success: false,
      error: 'Validation failed',
      details: errors.array()
    });
  }
  
  const { title, description, priority, status = 'todo', projectId, dueDate } = req.body;
  
  // Check if project exists and user has access
  const project = projects.get(projectId);
  if (!project) {
    throw new AppError('Project not found', 404);
  }
  
  if (req.user.role !== 'admin' && 
      project.createdBy !== req.user.id && 
      !project.team.includes(req.user.id)) {
    throw new AppError('Access denied to this project', 403);
  }
  
  const taskId = `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  const newTask = {
    title,
    description,
    priority,
    status,
    projectId,
    assignedTo: req.user.id,
    createdBy: req.user.id,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    ...(dueDate && { dueDate })
  };
  
  tasks.set(taskId, newTask);
  
  // Log task creation
  logger.audit('task_created', 'task', taskId, {
    title,
    projectId,
    createdBy: req.user.id
  });
  
  res.status(201).json({
    success: true,
    message: 'Task created successfully',
    data: {
      task: {
        id: taskId,
        ...newTask
      }
    }
  });
}));

/**
 * @route   GET /api/v1/tasks
 * @desc    Get tasks with filtering
 * @access  Private
 */
router.get('/tasks', requirePermission('read'), catchAsync(async (req, res) => {
  const {
    projectId,
    status,
    priority,
    assignedTo,
    page = 1,
    limit = 20
  } = req.query;
  
  let taskList = Array.from(tasks.entries()).map(([id, task]) => ({
    id,
    ...task
  }));
  
  // Filter by project access
  if (req.user.role !== 'admin') {
    const accessibleProjects = Array.from(projects.entries())
      .filter(([_, project]) => 
        project.createdBy === req.user.id || 
        project.team.includes(req.user.id)
      )
      .map(([id, _]) => id);
    
    taskList = taskList.filter(task => accessibleProjects.includes(task.projectId));
  }
  
  // Apply filters
  if (projectId) {
    taskList = taskList.filter(task => task.projectId === projectId);
  }
  
  if (status) {
    taskList = taskList.filter(task => task.status === status);
  }
  
  if (priority) {
    taskList = taskList.filter(task => task.priority === priority);
  }
  
  if (assignedTo) {
    taskList = taskList.filter(task => task.assignedTo === assignedTo);
  }
  
  // Apply pagination
  const startIndex = (page - 1) * limit;
  const endIndex = startIndex + parseInt(limit);
  const paginatedTasks = taskList.slice(startIndex, endIndex);
  
  res.json({
    success: true,
    data: {
      tasks: paginatedTasks,
      pagination: {
        currentPage: parseInt(page),
        totalPages: Math.ceil(taskList.length / limit),
        totalTasks: taskList.length,
        limit: parseInt(limit)
      }
    }
  });
}));

/**
 * @route   GET /api/v1/dashboard
 * @desc    Get dashboard overview
 * @access  Private
 */
router.get('/dashboard', requirePermission('read'), catchAsync(async (req, res) => {
  // Get user's projects
  const userProjects = Array.from(projects.entries())
    .filter(([_, project]) => 
      req.user.role === 'admin' || 
      project.createdBy === req.user.id || 
      project.team.includes(req.user.id)
    )
    .map(([id, project]) => ({ id, ...project }));
  
  // Get user's tasks
  const projectIds = userProjects.map(p => p.id);
  const userTasks = Array.from(tasks.entries())
    .filter(([_, task]) => projectIds.includes(task.projectId))
    .map(([id, task]) => ({ id, ...task }));
  
  // Calculate statistics
  const stats = {
    projects: {
      total: userProjects.length,
      active: userProjects.filter(p => p.status === 'active').length,
      completed: userProjects.filter(p => p.status === 'completed').length
    },
    tasks: {
      total: userTasks.length,
      todo: userTasks.filter(t => t.status === 'todo').length,
      inProgress: userTasks.filter(t => t.status === 'in_progress').length,
      review: userTasks.filter(t => t.status === 'review').length,
      done: userTasks.filter(t => t.status === 'done').length,
      overdue: userTasks.filter(t => 
        t.dueDate && new Date(t.dueDate) < new Date() && t.status !== 'done'
      ).length
    },
    recentActivity: {
      projects: userProjects
        .sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt))
        .slice(0, 5),
      tasks: userTasks
        .sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt))
        .slice(0, 10)
    }
  };
  
  res.json({
    success: true,
    data: { dashboard: stats }
  });
}));

module.exports = router;
