// MongoDB initialization script
// This script runs when the MongoDB container is first created

// Switch to the application database
db = db.getSiblingDB('system_architect_generator');

// Create collections with validation schemas
db.createCollection('users', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['user_id', 'username', 'email', 'created_at'],
      properties: {
        user_id: {
          bsonType: 'string',
          description: 'Unique user identifier'
        },
        username: {
          bsonType: 'string',
          description: 'Username must be a string and is required'
        },
        email: {
          bsonType: 'string',
          pattern: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$',
          description: 'Must be a valid email address'
        },
        full_name: {
          bsonType: ['string', 'null'],
          description: 'User full name (optional)'
        },
        created_at: {
          bsonType: 'date',
          description: 'User creation timestamp'
        },
        updated_at: {
          bsonType: 'date',
          description: 'User last update timestamp'
        },
        is_active: {
          bsonType: 'bool',
          description: 'User active status'
        }
      }
    }
  }
});

db.createCollection('projects', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['project_id', 'user_id', 'name', 'created_at'],
      properties: {
        project_id: {
          bsonType: 'string',
          description: 'Unique project identifier'
        },
        user_id: {
          bsonType: 'string',
          description: 'User ID who owns the project'
        },
        name: {
          bsonType: 'string',
          description: 'Project name'
        },
        description: {
          bsonType: 'string',
          description: 'Project description'
        },
        created_at: {
          bsonType: 'date',
          description: 'Project creation timestamp'
        },
        updated_at: {
          bsonType: 'date',
          description: 'Project last update timestamp'
        }
      }
    }
  }
});

db.createCollection('designs', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['design_id', 'project_id', 'user_id', 'created_at'],
      properties: {
        design_id: {
          bsonType: 'string',
          description: 'Unique design identifier'
        },
        project_id: {
          bsonType: 'string',
          description: 'Associated project ID'
        },
        user_id: {
          bsonType: 'string',
          description: 'User ID who created the design'
        },
        architecture_data: {
          bsonType: 'object',
          description: 'C4 architecture model data'
        },
        created_at: {
          bsonType: 'date',
          description: 'Design creation timestamp'
        },
        updated_at: {
          bsonType: 'date',
          description: 'Design last update timestamp'
        }
      }
    }
  }
});

db.createCollection('feedback', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['feedback_id', 'design_id', 'user_id', 'created_at'],
      properties: {
        feedback_id: {
          bsonType: 'string',
          description: 'Unique feedback identifier'
        },
        design_id: {
          bsonType: 'string',
          description: 'Associated design ID'
        },
        user_id: {
          bsonType: 'string',
          description: 'User ID who provided feedback'
        },
        content: {
          bsonType: 'string',
          description: 'Feedback content'
        },
        rating: {
          bsonType: 'int',
          minimum: 1,
          maximum: 5,
          description: 'Feedback rating (1-5)'
        },
        created_at: {
          bsonType: 'date',
          description: 'Feedback creation timestamp'
        }
      }
    }
  }
});

// Create indexes for better query performance
db.users.createIndex({ 'user_id': 1 }, { unique: true });
db.users.createIndex({ 'email': 1 }, { unique: true });
db.users.createIndex({ 'username': 1 });

db.projects.createIndex({ 'project_id': 1 }, { unique: true });
db.projects.createIndex({ 'user_id': 1 });
db.projects.createIndex({ 'created_at': -1 });

db.designs.createIndex({ 'design_id': 1 }, { unique: true });
db.designs.createIndex({ 'project_id': 1 });
db.designs.createIndex({ 'user_id': 1 });
db.designs.createIndex({ 'created_at': -1 });

db.feedback.createIndex({ 'feedback_id': 1 }, { unique: true });
db.feedback.createIndex({ 'design_id': 1 });
db.feedback.createIndex({ 'user_id': 1 });
db.feedback.createIndex({ 'created_at': -1 });

print('✓ Database initialized successfully');
print('✓ Collections created: users, projects, designs, feedback');
print('✓ Indexes created for optimal query performance');
