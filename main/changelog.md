# Changelog

### [Version 0.1.2]

### [16 December 2023]

- **Feature**: Asynchronous Fetching of Comics Data
  - Introduced an asynchronous function `fetch_comics_data` for fetching data from the comics API using `aiohttp`.
  - The function supports making asynchronous GET requests to the comics API with specified headers and parameters.
  - This enhances the application's performance by allowing asynchronous handling of API requests.

- **Project Management**
  - Organized tasks and TODO items in `TODO.md`.
  - Updated and reorganized changelog for better clarity.
  - Updated the 'README.md' for a more detailed description of the project.

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
