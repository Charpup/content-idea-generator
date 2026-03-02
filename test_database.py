"""
Test suite for Content Idea Generator Database Module
"""

import unittest
import tempfile
import os
from pathlib import Path

from database import ContentIdeaDatabase, DatabaseError, init_database


class TestDatabaseSchema(unittest.TestCase):
    """Test database schema creation and table existence"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.db = init_database(self.db_path)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_tables_exist(self):
        """Test that all required tables are created"""
        with self.db._get_connection() as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = {row['name'] for row in cursor.fetchall()}
        
        required_tables = {
            'categories', 'tags', 'content_items', 'content_tags',
            'text_snippets', 'snippet_tags', 'gold_sentences',
            'ideas', 'idea_relations', 'content_fts'
        }
        
        for table in required_tables:
            self.assertIn(table, tables, f"Table '{table}' should exist")
    
    def test_views_exist(self):
        """Test that all required views are created"""
        with self.db._get_connection() as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='view'"
            )
            views = {row['name'] for row in cursor.fetchall()}
        
        required_views = {
            'v_content_full', 'v_category_tree', 'v_ideas_ready', 'v_top_gold_sentences'
        }
        
        for view in required_views:
            self.assertIn(view, views, f"View '{view}' should exist")
    
    def test_triggers_exist(self):
        """Test that FTS5 sync triggers are created"""
        with self.db._get_connection() as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='trigger'"
            )
            triggers = {row['name'] for row in cursor.fetchall()}
        
        required_triggers = {
            'content_items_ai', 'content_items_au', 'content_items_ad',
            'categories_updated_at', 'content_items_updated_at', 'ideas_updated_at'
        }
        
        for trigger in required_triggers:
            self.assertIn(trigger, triggers, f"Trigger '{trigger}' should exist")
    
    def test_indexes_exist(self):
        """Test that indexes are created"""
        with self.db._get_connection() as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index'"
            )
            indexes = {row['name'] for row in cursor.fetchall()}
        
        required_indexes = {
            'idx_categories_parent', 'idx_categories_name',
            'idx_tags_name', 'idx_content_type', 'idx_content_category',
            'idx_content_status', 'idx_content_priority'
        }
        
        for index in required_indexes:
            self.assertIn(index, indexes, f"Index '{index}' should exist")
    
    def test_default_data_loaded(self):
        """Test that default categories and tags are loaded"""
        categories = self.db.list_categories()
        self.assertGreaterEqual(len(categories), 6, "Should have default categories")
        
        tags = self.db.list_tags()
        self.assertGreaterEqual(len(tags), 6, "Should have default tags")


class TestCategoriesCRUD(unittest.TestCase):
    """Test Categories CRUD operations"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.db = init_database(self.db_path)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_category(self):
        """Test creating a category"""
        cat_id = self.db.create_category("Test Category", "Test Description")
        self.assertIsNotNone(cat_id)
        self.assertIsInstance(cat_id, int)
        
        cat = self.db.get_category(cat_id)
        self.assertEqual(cat['name'], "Test Category")
        self.assertEqual(cat['description'], "Test Description")
    
    def test_create_subcategory(self):
        """Test creating hierarchical categories"""
        parent_id = self.db.create_category("Parent")
        child_id = self.db.create_category("Child", parent_id=parent_id)
        
        child = self.db.get_category(child_id)
        self.assertEqual(child['parent_id'], parent_id)
    
    def test_get_category_by_name(self):
        """Test retrieving category by name"""
        self.db.create_category("UniqueName")
        cat = self.db.get_category_by_name("UniqueName")
        self.assertIsNotNone(cat)
        self.assertEqual(cat['name'], "UniqueName")
    
    def test_update_category(self):
        """Test updating category"""
        cat_id = self.db.create_category("Old Name")
        result = self.db.update_category(cat_id, name="New Name", description="New Desc")
        self.assertTrue(result)
        
        cat = self.db.get_category(cat_id)
        self.assertEqual(cat['name'], "New Name")
        self.assertEqual(cat['description'], "New Desc")
    
    def test_delete_category(self):
        """Test deleting category"""
        cat_id = self.db.create_category("To Delete")
        result = self.db.delete_category(cat_id)
        self.assertTrue(result)
        
        cat = self.db.get_category(cat_id)
        self.assertIsNone(cat)
    
    def test_category_tree(self):
        """Test hierarchical category tree"""
        parent_id = self.db.create_category("Root")
        child_id = self.db.create_category("Child", parent_id=parent_id)
        grandchild_id = self.db.create_category("GrandChild", parent_id=child_id)
        
        tree = self.db.get_category_tree()
        self.assertGreaterEqual(len(tree), 3)
        
        paths = [item['path'] for item in tree]
        self.assertIn("Root", paths)
        self.assertIn("Root > Child", paths)
        self.assertIn("Root > Child > GrandChild", paths)


class TestTagsCRUD(unittest.TestCase):
    """Test Tags CRUD operations"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.db = init_database(self.db_path)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_tag(self):
        """Test creating a tag"""
        tag_id = self.db.create_tag("test-tag", color="#ff0000", description="Test tag")
        self.assertIsNotNone(tag_id)
        
        tag = self.db.get_tag(tag_id)
        self.assertEqual(tag['name'], "test-tag")
        self.assertEqual(tag['color'], "#ff0000")
    
    def test_get_tag_by_name(self):
        """Test retrieving tag by name"""
        self.db.create_tag("FindMe")
        tag = self.db.get_tag_by_name("FindMe")
        self.assertIsNotNone(tag)
        self.assertEqual(tag['name'], "FindMe")
    
    def test_update_tag(self):
        """Test updating tag"""
        tag_id = self.db.create_tag("OldTag")
        result = self.db.update_tag(tag_id, name="NewTag", color="#00ff00")
        self.assertTrue(result)
        
        tag = self.db.get_tag(tag_id)
        self.assertEqual(tag['name'], "NewTag")
        self.assertEqual(tag['color'], "#00ff00")
    
    def test_delete_tag(self):
        """Test deleting tag"""
        tag_id = self.db.create_tag("DeleteMe")
        result = self.db.delete_tag(tag_id)
        self.assertTrue(result)
        
        tag = self.db.get_tag(tag_id)
        self.assertIsNone(tag)
    
    def test_list_tags(self):
        """Test listing all tags"""
        self.db.create_tag("Tag1")
        self.db.create_tag("Tag2")
        self.db.create_tag("Tag3")
        
        tags = self.db.list_tags()
        tag_names = [t['name'] for t in tags]
        self.assertIn("Tag1", tag_names)
        self.assertIn("Tag2", tag_names)
        self.assertIn("Tag3", tag_names)


class TestContentItemsCRUD(unittest.TestCase):
    """Test Content Items CRUD operations"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.db = init_database(self.db_path)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_content_item(self):
        """Test creating content item"""
        content_id = self.db.create_content_item(
            type='article',
            title='Test Article',
            content='This is test content',
            source='https://example.com',
            author='Test Author'
        )
        self.assertIsNotNone(content_id)
        
        content = self.db.get_content_item(content_id)
        self.assertEqual(content['title'], 'Test Article')
        self.assertEqual(content['type'], 'article')
    
    def test_create_content_with_tags(self):
        """Test creating content with tags"""
        tag1 = self.db.create_tag("Tag1")
        tag2 = self.db.create_tag("Tag2")
        
        content_id = self.db.create_content_item(
            type='note',
            title='Tagged Note',
            tag_ids=[tag1, tag2]
        )
        
        content = self.db.get_content_item(content_id)
        self.assertIn("Tag1", content['tags'])
        self.assertIn("Tag2", content['tags'])
    
    def test_update_content_item(self):
        """Test updating content item"""
        content_id = self.db.create_content_item(
            type='note',
            title='Original Title'
        )
        
        result = self.db.update_content_item(
            content_id,
            title='Updated Title',
            priority=5
        )
        self.assertTrue(result)
        
        content = self.db.get_content_item(content_id)
        self.assertEqual(content['title'], 'Updated Title')
        self.assertEqual(content['priority'], 5)
    
    def test_delete_content_item(self):
        """Test deleting content item"""
        content_id = self.db.create_content_item(
            type='note',
            title='To Delete'
        )
        
        result = self.db.delete_content_item(content_id)
        self.assertTrue(result)
        
        content = self.db.get_content_item(content_id)
        self.assertIsNone(content)
    
    def test_list_content_with_filters(self):
        """Test listing content with filters"""
        self.db.create_content_item(type='article', title='Article 1')
        self.db.create_content_item(type='article', title='Article 2')
        self.db.create_content_item(type='book', title='Book 1')
        
        articles = self.db.list_content_items(type='article')
        self.assertEqual(len(articles), 2)
        
        books = self.db.list_content_items(type='book')
        self.assertEqual(len(books), 1)


class TestFullTextSearch(unittest.TestCase):
    """Test FTS5 full-text search functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.db = init_database(self.db_path)
        
        # Create test content
        self.db.create_content_item(
            type='article',
            title='Python Programming',
            content='Python is a great language for beginners and experts alike.'
        )
        self.db.create_content_item(
            type='article',
            title='Machine Learning Basics',
            content='Machine learning uses Python extensively for data analysis.'
        )
        self.db.create_content_item(
            type='book',
            title='The Art of Cooking',
            content='Cooking is an art that requires practice and patience.'
        )
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_search_content(self):
        """Test basic full-text search"""
        results = self.db.search_content('Python')
        self.assertGreaterEqual(len(results), 2)
        
        for result in results:
            self.assertIn('rank', result)
    
    def test_search_with_and(self):
        """Test search with AND operator"""
        results = self.db.search_content('Python AND beginners')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Python Programming')
    
    def test_search_with_snippet(self):
        """Test search with highlighted snippets"""
        results = self.db.search_with_snippet('Python')
        self.assertGreaterEqual(len(results), 2)
        
        for result in results:
            self.assertIn('title_highlight', result)
            self.assertIn('content_preview', result)
    
    def test_search_ranking(self):
        """Test that search results are ranked"""
        results = self.db.search_content('Python')
        self.assertGreaterEqual(len(results), 2)
        
        # Results should be ordered by rank
        ranks = [r['rank'] for r in results]
        self.assertEqual(ranks, sorted(ranks))


class TestTextSnippetsCRUD(unittest.TestCase):
    """Test Text Snippets CRUD operations"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.db = init_database(self.db_path)
        
        self.content_id = self.db.create_content_item(
            type='book',
            title='Test Book'
        )
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_snippet(self):
        """Test creating text snippet"""
        snippet_id = self.db.create_text_snippet(
            content_id=self.content_id,
            snippet_text='This is an important quote.',
            context='Chapter 1',
            page_ref='p. 42'
        )
        self.assertIsNotNone(snippet_id)
        
        snippet = self.db.get_text_snippet(snippet_id)
        self.assertEqual(snippet['snippet_text'], 'This is an important quote.')
        self.assertEqual(snippet['page_ref'], 'p. 42')
    
    def test_list_snippets(self):
        """Test listing snippets for content"""
        self.db.create_text_snippet(self.content_id, 'Snippet 1', position=1)
        self.db.create_text_snippet(self.content_id, 'Snippet 2', position=2)
        
        snippets = self.db.list_text_snippets(self.content_id)
        self.assertEqual(len(snippets), 2)


class TestGoldSentencesCRUD(unittest.TestCase):
    """Test Gold Sentences CRUD operations"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.db = init_database(self.db_path)
        
        self.content_id = self.db.create_content_item(
            type='article',
            title='Test Article'
        )
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_gold_sentence(self):
        """Test creating gold sentence"""
        sentence_id = self.db.create_gold_sentence(
            content_id=self.content_id,
            sentence='This is a golden sentence.',
            rating=5
        )
        self.assertIsNotNone(sentence_id)
        
        sentence = self.db.get_gold_sentence(sentence_id)
        self.assertEqual(sentence['sentence'], 'This is a golden sentence.')
        self.assertEqual(sentence['rating'], 5)
        self.assertEqual(sentence['usage_count'], 0)
    
    def test_increment_usage(self):
        """Test incrementing usage count"""
        sentence_id = self.db.create_gold_sentence(
            content_id=self.content_id,
            sentence='Test sentence'
        )
        
        result = self.db.increment_gold_sentence_usage(sentence_id)
        self.assertTrue(result)
        
        sentence = self.db.get_gold_sentence(sentence_id)
        self.assertEqual(sentence['usage_count'], 1)
        self.assertIsNotNone(sentence['last_used_at'])


class TestIdeasCRUD(unittest.TestCase):
    """Test Ideas CRUD operations"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.db = init_database(self.db_path)
        
        self.content_id = self.db.create_content_item(
            type='article',
            title='Source Article'
        )
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_idea(self):
        """Test creating idea"""
        idea_id = self.db.create_idea(
            content_id=self.content_id,
            concept='New Concept',
            elaboration='Detailed explanation here',
            use_cases=['Case 1', 'Case 2'],
            tags=['tag1', 'tag2'],
            priority=4,
            status='ready'
        )
        self.assertIsNotNone(idea_id)
        
        idea = self.db.get_idea(idea_id)
        self.assertEqual(idea['concept'], 'New Concept')
        self.assertEqual(idea['priority'], 4)
        self.assertEqual(idea['status'], 'ready')
        self.assertEqual(len(idea['use_cases']), 2)
        self.assertEqual(len(idea['tags']), 2)
    
    def test_list_ideas_by_status(self):
        """Test filtering ideas by status"""
        self.db.create_idea(self.content_id, 'Idea 1', status='new')
        self.db.create_idea(self.content_id, 'Idea 2', status='ready')
        self.db.create_idea(self.content_id, 'Idea 3', status='used')
        
        new_ideas = self.db.list_ideas(status='new')
        self.assertEqual(len(new_ideas), 1)
        
        ready_ideas = self.db.list_ideas(status='ready')
        self.assertEqual(len(ready_ideas), 1)


class TestIdeaRelations(unittest.TestCase):
    """Test Idea Relations functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.db = init_database(self.db_path)
        
        self.content_id = self.db.create_content_item(type='article', title='Test')
        self.idea1 = self.db.create_idea(self.content_id, 'Idea One')
        self.idea2 = self.db.create_idea(self.content_id, 'Idea Two')
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_relation(self):
        """Test creating relation between ideas"""
        result = self.db.create_idea_relation(
            self.idea1, self.idea2,
            relation_type='inspired_by',
            strength=4
        )
        self.assertTrue(result)
    
    def test_get_related_ideas(self):
        """Test getting related ideas"""
        self.db.create_idea_relation(self.idea1, self.idea2, 'builds_on', 5)
        
        related = self.db.get_related_ideas(self.idea1)
        self.assertEqual(len(related), 1)
        self.assertEqual(related[0]['concept'], 'Idea Two')
        self.assertEqual(related[0]['relation_type'], 'builds_on')
        self.assertEqual(related[0]['strength'], 5)


class TestObsidianExport(unittest.TestCase):
    """Test Obsidian Markdown export functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.db = init_database(self.db_path)
        
        self.content_id = self.db.create_content_item(
            type='article',
            title='Test Article for Export',
            content='This is the main content.',
            author='Test Author',
            source='https://example.com'
        )
        
        self.db.create_text_snippet(
            self.content_id,
            'Important quote here.',
            context='Introduction',
            position=1
        )
        
        self.db.create_gold_sentence(
            self.content_id,
            'Golden sentence for reuse.',
            rating=5
        )
        
        self.idea_id = self.db.create_idea(
            self.content_id,
            'Exportable Idea',
            elaboration='This idea is worth exporting.',
            use_cases=['Case A', 'Case B'],
            priority=4
        )
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_export_content_to_markdown(self):
        """Test exporting content to Markdown"""
        md = self.db.export_content_to_markdown(self.content_id)
        self.assertIsNotNone(md)
        
        # Check markdown contains expected elements
        self.assertIn('# Test Article for Export', md)
        self.assertIn('**Type:** article', md)
        self.assertIn('**Author:** Test Author', md)
        self.assertIn('## Snippets', md)
        self.assertIn('Important quote here.', md)
        self.assertIn('## Gold Sentences', md)
        self.assertIn('Golden sentence for reuse.', md)
        self.assertIn('## Ideas', md)
        self.assertIn('Exportable Idea', md)
    
    def test_export_idea_to_markdown(self):
        """Test exporting idea to Markdown"""
        md = self.db.export_idea_to_markdown(self.idea_id)
        self.assertIsNotNone(md)
        
        self.assertIn('# Idea: Exportable Idea', md)
        self.assertIn('**Priority:** 4/5', md)
        self.assertIn('## Elaboration', md)
        self.assertIn('This idea is worth exporting.', md)
        self.assertIn('## Use Cases', md)
        self.assertIn('- Case A', md)
    
    def test_export_all_content(self):
        """Test bulk export to directory"""
        export_dir = os.path.join(self.temp_dir, 'export')
        counts = self.db.export_all_content(export_dir)
        
        self.assertEqual(counts['content'], 1)
        self.assertEqual(counts['ideas'], 1)
        
        # Check files were created
        self.assertTrue(os.path.exists(export_dir))
        md_files = list(Path(export_dir).glob('*.md'))
        self.assertEqual(len(md_files), 1)
        
        ideas_dir = Path(export_dir) / 'ideas'
        self.assertTrue(ideas_dir.exists())
        idea_files = list(ideas_dir.glob('*.md'))
        self.assertEqual(len(idea_files), 1)


class TestStatistics(unittest.TestCase):
    """Test database statistics"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.db = init_database(self.db_path)
        
        # Create some test data
        self.db.create_category("Cat 1")
        self.db.create_tag("Tag 1")
        
        content_id = self.db.create_content_item(type='article', title='Article 1')
        self.db.create_content_item(type='book', title='Book 1')
        
        self.db.create_idea(content_id, 'Idea 1', status='new')
        self.db.create_idea(content_id, 'Idea 2', status='ready')
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_get_statistics(self):
        """Test getting database statistics"""
        stats = self.db.get_statistics()
        
        self.assertIn('categories', stats)
        self.assertIn('tags', stats)
        self.assertIn('content_items', stats)
        self.assertIn('ideas', stats)
        
        self.assertGreaterEqual(stats['categories'], 1)
        self.assertGreaterEqual(stats['tags'], 1)
        self.assertEqual(stats['content_items'], 2)
        self.assertEqual(stats['ideas'], 2)
        
        # Check content by type
        self.assertIn('content_by_type', stats)
        self.assertEqual(stats['content_by_type'].get('article'), 1)
        self.assertEqual(stats['content_by_type'].get('book'), 1)
        
        # Check ideas by status
        self.assertIn('ideas_by_status', stats)


class TestErrorHandling(unittest.TestCase):
    """Test error handling"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.db = init_database(self.db_path)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_invalid_content_type(self):
        """Test that invalid content type is rejected"""
        with self.assertRaises(DatabaseError):
            self.db.create_content_item(
                type='invalid_type',
                title='Test'
            )
    
    def test_invalid_priority(self):
        """Test that invalid priority is rejected"""
        with self.assertRaises(DatabaseError):
            self.db.create_content_item(
                type='note',
                title='Test',
                priority=10  # Should be 1-5
            )


def run_tests():
    """Run all tests and return results"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestDatabaseSchema,
        TestCategoriesCRUD,
        TestTagsCRUD,
        TestContentItemsCRUD,
        TestFullTextSearch,
        TestTextSnippetsCRUD,
        TestGoldSentencesCRUD,
        TestIdeasCRUD,
        TestIdeaRelations,
        TestObsidianExport,
        TestStatistics,
        TestErrorHandling
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
