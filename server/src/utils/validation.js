const logger = require('./logger');

/**
 * Validate required environment variables
 */
function validateEnvironment() {
  const requiredEnvVars = [
    'NODE_ENV',
    'DATABASE_URL',
    'REDIS_URL'
  ];

  const missingVars = requiredEnvVars.filter(varName => !process.env[varName]);

  if (missingVars.length > 0) {
    logger.error(`Missing required environment variables: ${missingVars.join(', ')}`);
    logger.error('Please check your .env file or environment configuration');
    process.exit(1);
  }

  // Validate NODE_ENV
  const validEnvs = ['development', 'production', 'test'];
  if (!validEnvs.includes(process.env.NODE_ENV)) {
    logger.error(`Invalid NODE_ENV: ${process.env.NODE_ENV}. Must be one of: ${validEnvs.join(', ')}`);
    process.exit(1);
  }

  // Validate DATABASE_URL format
  if (!process.env.DATABASE_URL.startsWith('postgresql://')) {
    logger.error('DATABASE_URL must be a valid PostgreSQL connection string');
    process.exit(1);
  }

  // Validate REDIS_URL format
  if (!process.env.REDIS_URL.startsWith('redis://')) {
    logger.error('REDIS_URL must be a valid Redis connection string');
    process.exit(1);
  }

  logger.info('Environment validation passed');
}

/**
 * Validate API request data using Joi schemas
 */
function validateRequest(schema) {
  return (req, res, next) => {
    const { error, value } = schema.validate(req.body);
    
    if (error) {
      return res.status(400).json({
        error: 'Validation error',
        details: error.details.map(detail => detail.message)
      });
    }
    
    req.validatedData = value;
    next();
  };
}

/**
 * Validate query parameters
 */
function validateQuery(schema) {
  return (req, res, next) => {
    const { error, value } = schema.validate(req.query);
    
    if (error) {
      return res.status(400).json({
        error: 'Query validation error',
        details: error.details.map(detail => detail.message)
      });
    }
    
    req.validatedQuery = value;
    next();
  };
}

module.exports = {
  validateEnvironment,
  validateRequest,
  validateQuery
};
