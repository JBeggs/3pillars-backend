#!/bin/bash
# Railway setup script for Django CRM
# Run with: railway run ./railway_setup.sh

echo "Running migrations..."
python manage.py migrate

echo "Loading initial data..."
python manage.py loaddata \
    country.json currency.json groups.json resolution.json \
    department.json deal_stage.json projectstage.json taskstage.json \
    client_type.json closing_reason.json industry.json lead_source.json \
    publicemaildomain.json help_en.json sites.json reminders.json \
    massmailsettings.json

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Create superuser: railway run python manage.py createsuperuser"
echo "2. Your app should be running at: https://your-app.railway.app"
echo "3. API docs: https://your-app.railway.app/api/docs/"

