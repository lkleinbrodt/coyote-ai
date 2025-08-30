# Character Explorer Ingestion Guide

This guide will walk you through how to ingest new books into your Character Explorer database using the CLI command we've built.

## Prerequisites

1. **Database Setup**: Ensure your PostgreSQL database is running and the character explorer tables have been created (this should already be done from our implementation)
2. **Virtual Environment**: Make sure you're in the virtual environment: `source venv/bin/activate`
3. **Dependencies**: All required packages should be installed (sentence-transformers, pgvector, etc.)

## Step 1: Prepare Your Book Text File

You'll need a plain text file containing the full text of the book you want to ingest.

### Getting Book Text

**Option A: Project Gutenberg**

```bash
# Download a book from Project Gutenberg
curl -o emma.txt "https://www.gutenberg.org/files/158/158-0.txt"
```

**Option B: Manual Text File**

- Create a `.txt` file with the book content
- Ensure it's UTF-8 encoded
- Remove any headers, footers, or non-book content

### Example Book Files

```
books/
├── emma.txt          # Jane Austen's Emma
├── pride_prejudice.txt
├── great_gatsby.txt
└── moby_dick.txt
```

## Step 2: Run the Ingestion Command

The ingestion command now automatically extracts the book title and author from the first 50 lines of the text file using an LLM.

### Basic Usage

```bash
flask ingest-book <filepath>
```

The command will automatically:

1. Extract title and author from the text
2. Check if the book already exists
3. Process the dialogue and generate embeddings
4. Save everything to the database

### Examples

**Ingest Emma (automatic metadata extraction):**

```bash
flask ingest-book books/emma.txt
```

**Ingest with manual override:**

```bash
flask ingest-book books/emma.txt --title "Emma" --author "Jane Austen"
```

**Force re-ingest an existing book:**

```bash
flask ingest-book books/emma.txt --force
```

## Step 3: Monitor the Ingestion Process

The command will provide real-time feedback:

```
Starting ingestion from books/emma.txt...
Extracting book metadata...
Extracted: 'Emma' by Jane Austen
Extracting dialogue... (this may take a while)
Processing chunk 1/45...
Processing chunk 2/45...
...
Extracted 1,247 dialogue entries. Processing characters...
Found 23 unique characters. Generating embeddings and saving...
  - Processed Emma Woodhouse with 156 quotes.
  - Processed Mr. Knightley with 89 quotes.
  - Processed Harriet Smith with 67 quotes.
  ...
Successfully ingested 'Emma' with 15 characters.
```

## Step 4: Verify the Ingestion

You can verify the data was ingested correctly by:

### Check the Database

```sql
-- Connect to your PostgreSQL database
psql -U coyote-user -d coyote-db-dev

-- Check books
SELECT * FROM character_explorer.books;

-- Check characters
SELECT name, total_quotes, book_id FROM character_explorer.characters LIMIT 10;

-- Check quotes
SELECT COUNT(*) FROM character_explorer.quotes;
```

### Test the API

```bash
# Test the search endpoint
curl -H "Authorization: Bearer <your-jwt-token>" \
     "http://localhost:5000/character-explorer/search?q=Emma"

# Test the random character endpoint
curl -H "Authorization: Bearer <your-jwt-token>" \
     "http://localhost:5000/character-explorer/random"
```

## Troubleshooting

### Common Issues

**1. File Not Found**

```
Error: File not found at books/emma.txt
```

**Solution**: Check the file path and ensure the file exists.

**2. Book Already Exists**

```
Book 'Emma' already exists in the database. Use --force to re-ingest.
```

**Solution**: Use the `--force` flag to re-ingest, or use a different title.

**3. Metadata Extraction Failed**

```
Error: Could not extract book metadata. Please provide --title and --author manually.
```

**Solution**:

- Check if the text file has proper headers/title information
- Provide the title and author manually using `--title` and `--author` flags
- Ensure the first 50 lines contain book metadata

**4. No Dialogue Extracted**

```
No dialogue could be extracted. Aborting.
```

**Solution**:

- Check if the text file contains dialogue
- Ensure the text is properly formatted
- Try a different book or check the text quality

**5. LLM API Errors**

```
Could not parse LLM response for chunk 1: ...
```

**Solution**:

- Check your OpenRouter API key is set
- Ensure you have sufficient API credits
- The system will continue with other chunks even if some fail

### Debugging Tips

**1. Check Logs**

The ingestion process provides detailed logging. Look for:

- Number of chunks processed
- Number of dialogue entries extracted
- Number of characters found
- Any error messages

**2. Monitor Database**

```sql
-- Check if data is being inserted
SELECT COUNT(*) FROM character_explorer.books;
SELECT COUNT(*) FROM character_explorer.characters;
SELECT COUNT(*) FROM character_explorer.quotes;
```

**3. Test with Small Files**

Start with shorter texts or excerpts to test the pipeline before running on full novels.

## Advanced Usage

### Batch Processing Multiple Books

Create a script to process multiple books:

```bash
#!/bin/bash
# ingest_multiple_books.sh

books=(
    "books/emma.txt"
    "books/pride_prejudice.txt"
    "books/great_gatsby.txt"
)

for book in "${books[@]}"; do
    echo "Processing $book..."
    flask ingest-book "$book"
    echo "Completed $book"
    echo "---"
done
```

### Manual Override Examples

If automatic extraction fails, you can manually specify metadata:

```bash
# Override just the title
flask ingest-book books/emma.txt --title "Emma"

# Override just the author
flask ingest-book books/emma.txt --author "Jane Austen"

# Override both
flask ingest-book books/emma.txt --title "Emma" --author "Jane Austen"
```

### Customizing the Process

**Adjust Chunk Size** (in `backend/character_explorer/services/dialogue_extractor.py`):

```python
self.chunk_size = 4000  # Increase for longer chunks, decrease for shorter
```

**Adjust Minimum Quote Length** (in `backend/character_explorer/services/dialogue_extractor.py`):

```python
if len(quote.split()) >= 10:  # Change minimum word count
```

**Adjust Minimum Character Quotes** (in `backend/character_explorer/ingest.py`):

```python
if len(quotes_list) < 5:  # Change minimum quotes per character
```

## Performance Considerations

### Large Books

- **Emma** (~500KB): ~5-10 minutes
- **War and Peace** (~3MB): ~30-60 minutes
- **Ulysses** (~1.5MB): ~20-30 minutes

### Resource Usage

- **Memory**: ~2-4GB RAM for large books
- **API Calls**: ~1 call per 4000 characters + 1 call for metadata extraction
- **Database**: Embeddings are ~1.5KB per quote

### Optimization Tips

1. **Process during off-peak hours** to avoid API rate limits
2. **Monitor API usage** to stay within limits
3. **Use smaller chunk sizes** for books with complex dialogue
4. **Consider processing in batches** for very large books

## Example Workflow

Here's a complete example of ingesting a new book:

```bash
# 1. Download a book
curl -o books/emma.txt "https://www.gutenberg.org/files/158/158-0.txt"

# 2. Activate virtual environment
source venv/bin/activate

# 3. Ingest the book (automatic metadata extraction)
flask ingest-book books/emma.txt

# 4. Test the results
curl -H "Authorization: Bearer <token>" \
     "http://localhost:5000/character-explorer/search?q=Emma"
```

## Next Steps

After ingesting books, you can:

1. **Test the frontend** by visiting `/character-explorer`
2. **Search for characters** and find similar ones
3. **View representative quotes** for each character
4. **Add more books** to expand your character database

The ingestion framework is designed to be robust and handle various text formats, but always verify the results and adjust parameters as needed for your specific use case.

## API Endpoints Reference

Once books are ingested, you can use these endpoints:

- `GET /character-explorer/search?q=<query>` - Search characters by name
- `GET /character-explorer/random` - Get a random character
- `GET /character-explorer/<id>/similar` - Find similar characters
- `GET /character-explorer/<id>/quotes` - Get character quotes
- `GET /character-explorer/books` - List all books

All endpoints require JWT authentication.
