Repo Radar
Repo Radar is a GitHub activity tracker that helps developers stay on top of recent activity across multiple repositories. The app fetches and displays open pull requests, recent commits, and repository changes in a simple, easy-to-understand interface. It helps teams monitor activity and keep track of contributions across their codebase, all in one place.

Features
Track Multiple Repositories: Monitor several repositories at once, either by organization or personal account.

Recent Activity: See recent commits and pull requests in real-time.

Custom Filters: Filter repositories and commits based on specific branches.

User-friendly Interface: Dynamic layout that adjusts depending on how many repositories are selected.

Main Branch Highlighting: Commits to the main branch are highlighted for easy identification.

How It Works
Authentication: The app uses GitHub's API and requires a personal access token for authentication.

Fetching Data: The app fetches open pull requests and commits from selected repositories.

Dynamic Display: Repositories are displayed in a grid layout, with the option to filter by repository or branch.

Notifications: The app highlights main branch commits in red to ensure they stand out.

Collaboration
This project is the result of a collaborative effort, with the main design and development done by me, Cody Cook. I used a combination of Python, Flask, and GitHub's API to create a dynamic and useful tool for tracking repository activity. Throughout the development process, I was assisted by ChatGPT (a language model developed by OpenAI), which helped me refine ideas, answer technical questions, and optimize code. The final result is a user-friendly tool that meets the needs of developers and teams managing multiple repositories.

Special thanks to ChatGPT for providing invaluable assistance throughout the project.

Installation
Clone the repository:

bash
Copy
git clone https://github.com/CodyCookCodes/RepoRadar.git
Install dependencies:

bash
Copy
pip install -r requirements.txt
Run the application:

bash
Copy
python app.py
The application will automatically set up the necessary environment variables and configuration for you. Visit http://127.0.0.1:5000 in your web browser to start using the app.

Usage
Once authenticated, you can choose which repositories to monitor.

The app will display the recent commits and open pull requests for each repository.

The interface allows you to filter by repository and branch.

Contributions
Feel free to contribute to this project by opening issues or submitting pull requests. Any improvements or new features are welcome!

Acknowledgments
GitHub: For providing the API that powers this app.

ChatGPT: For assisting in brainstorming, answering technical questions, and helping to optimize the code throughout the development of the project.

Notes:
I’ve kept the project setup simple, with no need for the user to manually handle .env files. The application sets up everything automatically for the user.
