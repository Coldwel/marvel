# Changelog

## [Version 0.1.6]

### [1 April 2024]

- **Feature**: User Login and Registration
  - Implemented user login and registration functionality with database integration.
  - Added a login section below the search bar on the main screen.
  - Users can enter their username (email) and password to log in.
  - Provided a "Register" button that opens a registration window for new users.
  - The registration window includes fields for name, email, password, and password confirmation.
  - User information is securely stored in the database upon successful registration.
  - Login credentials are validated against the database to authenticate users.
  - Upon successful login, the login section is hidden, and a welcome message is displayed.
  - Improved error handling and user feedback for login and registration processes.

- **Feature**: Favorite List Functionality
  - Implemented a favorite list feature that allows users to add and remove comics from their favorites.
  - Added a "Favorite List" button that appears in the top left corner after a successful login.
  - Clicking the "Favorite List" button opens a new window displaying the user's favorite comics.
  - Each comic in the favorites window includes a "Remove" button to remove the comic from the list and the database.
  - Updated the database schema to include a "favorites" table that associates favorite comics with user IDs.
  - Modified the `SearchController` and `SearchView` classes to handle adding and removing comics from the favorites list.
  - Implemented scroll wheel functionality in the favorites window for improved navigation.

## [Version 0.1.5]

### [31 March 2024]

- **Feature**: Display Comic Prices
  - Added functionality to display the price of each comic book in the comics list.
  - Modified the `display_comic_page` method to extract the price value from the 'prices' dictionary in the comic_item.
  - Created a price_label using tk.Label to display the price value or "Price: N/A" if the price information is not available.
  - Positioned the price_label in the desired location within the new_comics_frame using grid.

## [Version 0.1.4]

### [30 March 2024]

- **Feature**: Pagination implemented
  - Introduced pagination functionality to the search results and comics list.
  - Added "Previous" and "Next" buttons to navigate through multiple pages of results.
  - Implemented logic to disable the "Previous" button on the first page and the "Next" button on the last page.
  - Updated the `display_comic_page` method to handle the creation and deletion of the comics frame correctly.
  - Resolved the `KeyError` issue when navigating through comic pages.

- **Readability Improvement**: Total class overhaul
  - Refactored the `SearchView` class for better code organization and readability.
  - Moved the `display_comic_page` method outside of the `display_comics_list` method and made it an instance method of the `SearchView` class.
  - Introduced the `change_comic_page` method to handle page navigation in the comics list.
  - Stored the `comics_list` as an instance variable in the `SearchView` class for easier access within methods.
  - Updated method signatures and calls to reflect the changes in the class structure.

## [Version 0.1.3]

### [19 December 2023]

- **Feature**: Asynchronous Fetching of Comics Data
  - Introduced an asynchronous function `fetch_comics_data` for fetching data from the comics API using `aiohttp`.
  - The function supports making asynchronous GET requests to the comics API with specified headers and parameters.
  - This enhances the application's performance by allowing asynchronous handling of API requests.

- **Project Management**
  - Organized tasks and TODO items in `TODO.md`.
  - Updated and reorganized changelog for better clarity.
  - Updated the 'README.md' for a more detailed description of the project.

## [Version 0.1.2]

### [14-15 December 2023]

- **Method Name Change**: Renamed `show_comic_window` method to `retrieve_and_display_comics` for clarity in functionality.
- **Scrollbar Enhancement**: Updated the scrollbar in `display_comics_list` to fix its placement issue. It is now attached to comics canvas instead of comics window, addressing the tiny scrollbar in the lower right corner.
- **Comics List Descriptions**: Added descriptions to the comics list to display the API description of each comic.

### [12 December 2023]

- **Thumbnail Images**: Implemented thumbnail images for comics displayed in the list after pressing the 'comics' button.
- **Homescreen Improvement**: Added a static Marvel logo to the homescreen for a more visually appealing layout.
  - Created a new static image method to handle the logo.
- **Layout Adjustment**: Changed the homescreen layout to position the search bar under the logo.
  - Created the `setup_search_frame()` method to manage search elements.
  - Placed search elements using `place()` on both the homescreen and results screen.
  - Set focus to the `query_entry()` text box on the homescreen for user convenience.
  - Created a frame to organize search results for better layout control.
- **Scroll Wheel Functionality**: Enabled scroll wheel functionality anywhere the cursor was idle.
- **Debugging Enhancements**: Added debugging `print()` statements to the `search_api()` method for better troubleshooting.
