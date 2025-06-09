from django.db import models
import requests


class LichessAPIError(BaseException):
    pass


class Player(models.Model):

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256,
                            null=True,
                            blank=True)
    email = models.EmailField()
    country = models.CharField(max_length=2,
                               null=True,
                               blank=True)
    lichess_username = models.CharField(max_length=150,
                                        unique=True,
                                        blank=True, null=True)
    lichess_rating_bullet = models.IntegerField(default=0)
    lichess_rating_blitz = models.IntegerField(default=0)
    lichess_rating_rapid = models.IntegerField(default=0)
    lichess_rating_classical = models.IntegerField(default=0)
    fide_id = models.IntegerField(unique=True, default=None,
                                  blank=True, null=True)
    fide_rating_blitz = models.IntegerField(default=0)
    fide_rating_rapid = models.IntegerField(default=0)
    fide_rating_classical = models.IntegerField(default=0)
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def check_lichess_user_exists(self):

        if not self.lichess_username:
            return False

        url = f"https://lichess.org/api/user/{self.lichess_username}"
        response = requests.get(url)

        if response.status_code == 200:
            return True
        else:
            return False

    def get_lichess_user_ratings(self, *args, **kwargs):

        if not self.lichess_username:
            return False

        url = f"https://lichess.org/api/user/{self.lichess_username}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            self.lichess_rating_bullet = data['perfs']['bullet']['rating']
            self.lichess_rating_blitz = data['perfs']['blitz']['rating']
            self.lichess_rating_rapid = data['perfs']['rapid']['rating']
            self.lichess_rating_classical = \
                data['perfs']['classical']['rating']

        else:
            raise LichessAPIError()

    def save(self, *args, **kwargs):

        player = None

        if self.lichess_username:
            player = Player.objects.\
                filter(lichess_username=self.lichess_username).first()

        if not player and self.fide_id:
            player = Player.objects.filter(fide_id=self.fide_id).first()

        if not player and (self.name and self.email):
            player = Player.objects.\
                filter(name=self.name, email=self.email).first()

        if player:
            self.id = player.id
            for field in ['name', 'email', 'country', 'fide_id',
                          'fide_rating_blitz', 'fide_rating_rapid',
                          'fide_rating_classical']:
                value = getattr(self, field, None)
                if value:
                    setattr(player, field, value)

            self = player

        if self.lichess_username and self.check_lichess_user_exists():
            self.get_lichess_user_ratings()
        else:
            self.lichess_username = None
            super().save(*args, **kwargs)
            return

        super().save(*args, **kwargs)

    def __str__(self):

        if self.lichess_username is None:
            return "invalid_lichess_user"

        if self.lichess_username:
            return self.lichess_username

        return self.name
