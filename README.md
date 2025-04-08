# Image Labeling Tool

A desktop application for labeling images with Vietnamese questions and answers. This tool helps in creating and managing image-based question-answer pairs for various use cases.

## Features

- Create and edit Vietnamese questions for images
- Support for multiple question types (Existence Checking, Others)
- Tag-based organization system
- Answerable/Unanswerable question states
- Image source tracking
- QA source tracking
- Revert and confirm functionality for changes

## Demo Video 
https://github.com/user-attachments/assets/3852392c-74af-4ad8-93cb-2d589bcd589c
<div align="center"><strong>The Web Demo Video</strong></div>

## Prerequisites

- Python 3.8 or higher (I am run correctly with Python 3.10)
- PyQt5
- Conda (optional, for Conda installation method)

## Project Structure

```
image_labelling_tool/
├── src/
│   ├── main_vietnamese.py          # Main application entry point
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── components/
│   │   │   ├── __init__.py
│   │   │   ├── answer_input.py                # Hangle logic of entering answer
│   │   │   ├── confirmation_dialog.py         # Handle logic of confirming change from user
│   │   │   └── image_viewer.py                # Logic for loading image
│   │   │   ├── navigation.py                  # Logic for navigation
│   │   │   ├── title_display.py               # Handle logic of display LABEL/UNLABEL image
│   │   │   └── vietnamese_question_list.py    # The most important file handle main logics of the applications
│   │   └── vietnam_main_window.py         # Main application window - using for UI and saving data
│   └── logs/
│       ├── app.log        # Store log of running app - should be frequently deleted
├── data/
│   └── image                      # Store the collection of images
│   └── labels                     # Store the corresponding labels - auto-create when you save the first data points
├── requirements.txt               # Python package dependencies
├── README.md                      # Project documentation
└── .gitignore                     # Git ignore rules
```

## Installation

### Method 1: Using Conda (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd image_labelling_tool
```

2. Create and activate a new Conda environment:
```bash
# Create a new environment with Python 3.8
conda create -n ai4li python=3.8

# Activate the environment
conda activate ai4li

# Install PyQt5 and other dependencies
conda install -c conda-forge pyqt
conda install -c conda-forge sqlite
```

3. Install any remaining packages from requirements.txt:
```bash
pip install -r requirements.txt
```


## Usage

**1. Start the application:**
```bash
# Make sure your environment is activated
# For Conda:
conda activate ai4li


# Run the application
python src/main_vietnamese.py
```

**2. Main Interface Components:**

   **Default (store default value if user no change)**
   - Image Source: Select the source of the image
   - Question Type: Select the type of question (Existence Checking or Others)
   - Answerable: Default unanswerable no need to input answers
   - QA Source: Choose the source of the question-answer pair

   **Must-have (user must input these fields for data labelling)**

   - Question Input: Enter your Vietnamese question 
   - Tags: Add relevant tags to categorize questions
   - Answer Input: Enter the answer if answerable is True


**3. Working with Questions:**
   - Type your question in the question input field
   - Select appropriate question type
   - Add relevant tags using the tag search
   - Enter the answer or mark as unanswerable
   - Select appropriate sources

**4. Tag Management:**
   - Use the tag search field to find existing tags
   - Press Enter to add a new tag
   - Click the 'x' on a tag to remove it
   - Tags help organize and categorize questions

**5. Answer Management:**
   - Check "Có thể trả lời" if the question is answerable
   - Uncheck it if the question cannot be answered
   - For unanswerable questions, a default message will be set

**6. Revert and Confirm Functionality:**
   - **Confirm Button:**
     - Enabled only when there are actual changes to the question
     - Click to save all changes (question text, type, tags, answer, sources)
     - A confirmation dialog will show the changes before saving
     - After confirming, changes cannot be reverted

   - **Revert Button:**
     - Appears when there are unsaved changes
     - Click to discard all changes and restore the original state
     - Will reset:
       - Question text
       - Question type
       - Tags
       - Answer
       - Answerable state
       - Sources
     - After reverting, the confirm button will be disabled

   - **Change Detection:**
     - The system automatically detects changes in:
       - Question text
       - Question type
       - Tags (adding/removing)
       - Answer text
       - Answerable state
       - Image source
       - QA source
     - Buttons are automatically enabled/disabled based on changes

   - **Best Practices:**
     - Always review changes in the confirmation dialog before confirming
     - Use revert if you're unsure about changes
     - Save work frequently by confirming changes
     - The revert button is your safety net for undoing unwanted changes

## Notice and Testing

Due to the rapid development timeline, some parts of the application may not be optimal and could have potential bugs. Please follow these test cases to verify the core functionality before starting your work:

### Test Case 1: Labeling Unlabeled Data
1. Start the application
2. Select an unlabeled image
3. Enter a question
4. Add some tags
5. Set answerable state
6. Enter an answer
7. Click Confirm
8. Verify that:
   - The data is saved
   - The image is marked as labeled
   - The confirmation dialog shows correct information

### Test Case 2: Loading Labeled Data
1. Select the image you labeled in Test Case 1
2. Verify that:
   - Question text is loaded correctly
   - Tags are displayed properly
   - Answerable state is correct
   - Answer text is loaded
   - All sources are preserved

### Test Case 3: Editing Labeled Data
1. Select a labeled image
2. Make some changes:
   - Modify the question
   - Add/remove tags
   - Change answerable state
   - Edit answer
3. Test the Revert button:
   - Click Revert
   - Verify all changes are undone
   - Confirm button should be disabled

### Test Case 4: Saving Edited Data
1. Make changes to a labeled image
2. Click Confirm
3. Verify that:
   - Changes are saved
   - The confirmation dialog shows correct changes
   - The data persists after reloading

### Test Case 5: Navigation Testing
1. Try navigating between multiple images:
   - Use Next/Previous buttons
   - Check if images load properly
   - Verify that:
     - Labeled data loads correctly
     - Unlabeled data shows empty fields
     - Navigation is smooth without crashes



### If You Encounter Issues
1. Try restarting the application to see if you meet it again
3. Report any bugs to the repo owner with:
   - Steps to reproduce
   - Expected behavior
   - Actual behavior



