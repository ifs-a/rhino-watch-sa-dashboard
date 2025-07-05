# Rhino Watch SA Dashboard

🦏 **Wildlife Conservation Monitoring System**

A comprehensive dashboard for monitoring rhino poaching incidents in South Africa, deployed on Render.com's free tier.

## 🌟 Features

- **Real-time Incident Tracking**: Monitor and analyze rhino poaching incidents
- **Interactive Dashboard**: Statistics, charts, and incident mapping
- **API Endpoints**: RESTful API for data access and integration
- **User Authentication**: Secure login system with role-based access
- **Mobile Responsive**: Works perfectly on desktop and mobile devices
- **Free Deployment**: Runs on Render.com's generous free tier

## 🚀 Live Demo

**Dashboard URL**: [Your Render App URL will appear here after deployment]

**Default Login**:
- Username: `admin`
- Password: `RhinoWatch2025!`

## 📊 API Endpoints

- `GET /` - API information and status
- `GET /health` - Health check endpoint
- `GET /dashboard` - Web dashboard interface
- `GET /api/stats` - Dashboard statistics
- `GET /api/incidents` - List all incidents
- `GET /api/incidents/{id}` - Get specific incident
- `POST /api/auth/login` - User authentication

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **Database**: PostgreSQL (Render) / SQLite (fallback)
- **Authentication**: JWT tokens
- **Deployment**: Render.com
- **Frontend**: HTML/CSS/JavaScript

## 📈 Current Statistics

- **Total Incidents**: 5 sample incidents loaded
- **Verified Incidents**: 3 verified cases
- **Rhinos Affected**: 4 rhinos in sample data
- **Coverage**: All South African provinces

## 🔧 Deployment

This application is configured for automatic deployment on Render.com:

1. **Automatic Detection**: Render automatically detects the `render.yaml` configuration
2. **Database Setup**: PostgreSQL database is automatically provisioned
3. **Environment Variables**: Secret keys are automatically generated
4. **SSL Certificate**: HTTPS is automatically configured
5. **Auto-scaling**: Application scales to zero when not in use

## 🌍 Conservation Impact

This dashboard supports wildlife conservation efforts by:

- **Centralizing Data**: Aggregating incident reports from multiple sources
- **Real-time Monitoring**: Enabling rapid response to poaching activities
- **Data Analysis**: Providing insights for conservation strategy planning
- **Collaboration**: Facilitating information sharing between organizations
- **Transparency**: Making conservation data accessible to stakeholders

## 📝 Sample Data

The application includes sample incident data from 2024:

- Kruger National Park incidents
- Hluhluwe-iMfolozi Park monitoring
- Pilanesberg National Park cases
- Marakele National Park activities
- Addo Elephant National Park alerts

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt password protection
- **Environment Variables**: Secure configuration management
- **HTTPS Enforcement**: SSL/TLS encryption
- **CORS Protection**: Cross-origin request security

## 🆓 Zero-Cost Operation

This dashboard operates entirely within free tier limits:

- **Render.com**: 750 hours/month free hosting
- **PostgreSQL**: 1GB free database storage
- **SSL Certificate**: Free HTTPS encryption
- **Auto-scaling**: Scales to zero when inactive
- **Monitoring**: Built-in health checks and logging

## 📞 Support

For questions about wildlife conservation or technical support:

- **Conservation Organizations**: Contact your local wildlife protection agency
- **Technical Issues**: Check Render.com documentation
- **Data Sources**: DFFE, SANParks, Save the Rhino International

## 🌟 Contributing

This is an open-source conservation technology project. Contributions welcome for:

- Additional data source integrations
- Enhanced analytics and reporting
- Mobile application development
- Multi-language support
- Advanced mapping features

---

**Deployed with ❤️ for Wildlife Conservation**

*Protecting South Africa's rhinos through technology and collaboration*

