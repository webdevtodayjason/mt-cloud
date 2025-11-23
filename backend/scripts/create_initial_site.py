#!/usr/bin/env python3
"""
Create initial organization, client, and site for devices
"""
import sys
from pathlib import Path

backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.organization import Organization
from app.models.client import Client
from app.models.site import Site


def main():
    print("="*60)
    print("Creating Initial Site Structure")
    print("="*60)
    
    db = next(get_db())
    
    try:
        # Check if organization exists
        org = db.query(Organization).filter(Organization.slug == "titanium-computing").first()
        
        if not org:
            # Create organization
            org = Organization(
                name="Titanium Computing",
                slug="titanium-computing",
                plan_type="enterprise",
                max_devices=1000,
                is_active=True
            )
            db.add(org)
            db.commit()
            db.refresh(org)
            print(f"✅ Created organization: {org.name} (ID: {org.id})")
        else:
            print(f"✅ Organization exists: {org.name} (ID: {org.id})")
        
        # Check if client exists
        client = db.query(Client).filter(Client.name == "Internal Infrastructure").first()
        
        if not client:
            # Create client
            client = Client(
                organization_id=org.id,
                name="Internal Infrastructure",
                slug="internal-infrastructure",
                contact_email="admin@titaniumcomputing.com",
                contact_phone="",
                is_active=True
            )
            db.add(client)
            db.commit()
            db.refresh(client)
            print(f"✅ Created client: {client.name} (ID: {client.id})")
        else:
            print(f"✅ Client exists: {client.name} (ID: {client.id})")
        
        # Check if site exists
        site = db.query(Site).filter(Site.name == "Home Network").first()
        
        if not site:
            # Create site
            site = Site(
                client_id=client.id,
                name="Home Network",
                slug="home-network",
                address_line1="Local Network",
                city="",
                state="",
                zip_code="",
                country="USA",
                timezone="America/Chicago"
            )
            db.add(site)
            db.commit()
            db.refresh(site)
            print(f"✅ Created site: {site.name} (ID: {site.id})")
        else:
            print(f"✅ Site exists: {site.name} (ID: {site.id})")
        
        print("\n" + "="*60)
        print("Site structure ready!")
        print("="*60)
        print(f"\nOrganization: {org.name} (ID: {org.id})")
        print(f"Client: {client.name} (ID: {client.id})")
        print(f"Site: {site.name} (ID: {site.id})")
        print("\nYou can now run seed_devices.py to add devices.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
