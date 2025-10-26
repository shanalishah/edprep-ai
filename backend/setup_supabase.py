import os
from app.services.retrieval import TfidfRetriever


def main():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    # Choose a few representative PDFs (adjust paths if needed)
    pdfs = [
        os.path.abspath(os.path.join(project_root, '..', 'IELTS', 'Cambridge IELTS', 'Academic', 'Cambridge IELTS 15 with Answers Academic [www.luckyielts.com]', 'Cambridge IELTS 15 with Answers Academic [www.luckyielts.com].pdf')),
        os.path.abspath(os.path.join(project_root, '..', 'IELTS', 'Cambridge IELTS', 'Academic', 'Cambridge IELTS 16 with Answers Academic [www.luckyielts.com]', 'Cambridge IELTS 16 with Answers Academic [www.luckyielts.com].pdf')),
        os.path.abspath(os.path.join(project_root, '..', 'IELTS', 'Cambridge IELTS', 'Academic', 'Cambridge IELTS 20 with Answers Academic [www-1', 'Cambridge IELTS 20 with Answers Academic [www-1.pdf')),
    ]
    retriever = TfidfRetriever()
    retriever.index_pdfs(pdfs)
    out = os.path.join(project_root, 'models', 'retrieval_index.json')
    retriever.save(out)
    print(f"Saved retrieval index to {out}")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Script to set up Supabase database for IELTS Master Platform
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def setup_supabase_database():
    """Set up Supabase database with required tables"""
    
    # Get database URL from environment or prompt user
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL environment variable not set!")
        print("\n📋 Please set your Supabase database URL:")
        print("   export DATABASE_URL='postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres'")
        print("\n🔗 Get this from: Supabase Dashboard > Settings > Database")
        return False
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL: {version}")
        
        # Import and create tables
        print("📊 Creating database tables...")
        
        # Import models
        from app.models.user import User, UserProgress, UserSession
        from app.models.mentorship import (
            MentorshipConnection, MentorshipMessage, 
            MentorshipSession, UserProfile
        )
        from app.models.essay_submission import EssaySubmission
        
        # Create all tables
        from app.models.user import Base as UserBase
        from app.models.mentorship import Base as MentorshipBase
        from app.models.essay_submission import Base as EssayBase
        
        UserBase.metadata.create_all(bind=engine)
        MentorshipBase.metadata.create_all(bind=engine)
        EssayBase.metadata.create_all(bind=engine)
        
        print("✅ All database tables created successfully!")
        
        # Create admin accounts
        print("👤 Creating admin accounts...")
        create_admin_accounts(engine)
        
        return True
        
    except SQLAlchemyError as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def create_admin_accounts(engine):
    """Create admin accounts in Supabase"""
    from sqlalchemy.orm import sessionmaker
    from app.models.user import User
    import hashlib
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Admin accounts to create
        admin_accounts = [
            {
                "email": "admin1@edprep.ai",
                "username": "admin1",
                "full_name": "Admin User 1",
                "role": "admin"
            },
            {
                "email": "admin2@edprep.ai", 
                "username": "admin2",
                "full_name": "Admin User 2",
                "role": "mentor"
            },
            {
                "email": "admin3@edprep.ai",
                "username": "admin3", 
                "full_name": "Admin User 3",
                "role": "tutor"
            }
        ]
        
        for account in admin_accounts:
            # Check if user already exists
            existing_user = session.query(User).filter(
                (User.email == account["email"]) | (User.username == account["username"])
            ).first()
            
            if existing_user:
                print(f"⚠️  User {account['email']} already exists")
                continue
            
            # Create new user with plain text password for testing
            new_user = User(
                email=account["email"],
                username=account["username"],
                hashed_password="test",  # Plain text for testing
                full_name=account["full_name"],
                role=account["role"],
                is_verified=True
            )
            
            session.add(new_user)
            print(f"✅ Created {account['email']} ({account['role']})")
        
        session.commit()
        print("🎉 All admin accounts created successfully!")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error creating admin accounts: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    print("🚀 Setting up Supabase database for IELTS Master Platform...")
    print("=" * 60)
    
    success = setup_supabase_database()
    
    if success:
        print("\n🎉 Supabase setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Update your Railway environment variables with DATABASE_URL")
        print("2. Test the connection with your deployed backend")
        print("3. Your admin accounts are ready:")
        print("   - admin1@edprep.ai / test (admin)")
        print("   - admin2@edprep.ai / test (mentor)")
        print("   - admin3@edprep.ai / test (tutor)")
    else:
        print("\n❌ Supabase setup failed. Please check the errors above.")
        sys.exit(1)


