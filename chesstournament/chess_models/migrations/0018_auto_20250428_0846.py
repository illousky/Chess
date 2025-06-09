from django.db import migrations

def populate_ranking_systems(apps, schema_editor):
    RankingSystemClass = apps.get_model('chess_models', 'RankingSystemClass')
    systems = [
        ('BU', 'Buchholz'),
        ('BC', 'Buchholz Cut 1'),
        ('BA', 'Buchholz Average'),
        ('SB', 'Sonneborn-Berger'),
        ('PS', 'Plain Score'),
        ('WI', 'Wins'),
        ('BT', 'Black Times'),
    ]
    for value, _ in systems:
        RankingSystemClass.objects.get_or_create(value=value)

class Migration(migrations.Migration):

    dependencies = [
        ('chess_models', '0017_alter_tournament_referee'),  # ajusta esto
    ]

    operations = [
        migrations.RunPython(populate_ranking_systems),
    ]
