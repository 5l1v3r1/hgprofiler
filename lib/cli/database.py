import logging
import os
import shutil
import subprocess
import sys

from sqlalchemy.engine import reflection
from sqlalchemy.schema import (DropConstraint,
                               DropTable,
                               ForeignKeyConstraint,
                               MetaData,
                               Table)
from app.config import get_path
import app.database
import cli
from model import Base, Configuration, User, Site, File, Category
import model.user


class DatabaseCli(cli.BaseCli):
    ''' A tool for initializing the database. '''

    def _agnostic_bootstrap(self, config):
        ''' Bootstrap the Agnostic migrations system. '''

        env = {
            'AGNOSTIC_TYPE': 'postgres',
            'AGNOSTIC_HOST': config.get('database', 'host'),
            'AGNOSTIC_USER': config.get('database', 'super_username'),
            'AGNOSTIC_PASSWORD': config.get('database', 'super_password'),
            'AGNOSTIC_DATABASE': config.get('database', 'database'),
            'AGNOSTIC_MIGRATIONS_DIR': get_path('migrations'),
            'LANG': os.environ['LANG'],  # http://click.pocoo.org/4/python3/
            'PATH': os.environ['PATH'],
        }

        process = subprocess.Popen(
            ['agnostic', 'bootstrap'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            env=env
        )
        process.wait()

        if process.returncode != 0:
            args = (process.returncode, process.stderr.read().decode('ascii'))
            self._logger.error('External process `agnostic bootstrap` failed '
                               'with error code (%d):\n%s' % args)
            sys.exit(1)

    def _create_fixtures(self, config):
        ''' Create fixture data. '''

        self._create_fixture_configurations(config)
        self._create_fixture_images(config)
        self._create_fixture_users(config)
        self._create_fixture_sites(config)
        self._create_fixture_categories(config)

    def _create_fixture_configurations(self, config):
        ''' Create configurations. '''

        session = app.database.get_session(self._db)

        for key, value in config.items('config_table'):
            session.add(Configuration(key, value))

        session.commit()

    def _create_fixture_images(self, config):
        '''
        Create the generic error image.

        Since this script will often run as root, it modifies the owner of the
        new file to match the owner of the data directory.
        '''

        session = app.database.get_session(self._db)

        image_name = 'hgprofiler_error.png'
        data_stat = os.stat(get_path('data'))
        img_path = os.path.join(get_path('static'), 'img', image_name)
        with open(img_path, 'rb') as img:
            img_data = img.read()
            image_file = File(name=image_name, mime='image/png',
                              content=img_data)
            image_file.chown(data_stat.st_uid, data_stat.st_gid)
            session.add(image_file)

        session.commit()

    def _create_fixture_users(self, config):
        ''' Create user fixtures. '''

        session = app.database.get_session(self._db)
        hash_algorithm = config.get('password_hash', 'algorithm')

        try:
            hash_rounds = int(config.get('password_hash', 'rounds'))
        except:
            raise ValueError('Configuration value password_hash.rounds must'
                             ' be an integer: %s' % hash_rounds)

        admin = User('admin')
        admin.agency = 'Profiler'
        admin.name = 'Administrator'
        admin.is_admin = True
        admin.password_hash = model.user.hash_password(
            'MemexPass1',
            hash_algorithm,
            hash_rounds
        )
        session.add(admin)
        session.commit()

    def _create_fixture_sites(self, config):
        ''' Create site fixtures. '''

        session = app.database.get_session(self._db)

        about_me = Site(
            name='About.me',
            url='http://about.me/%s',
            status_code=200,
            test_username_pos='bob'
        )
        session.add(about_me)

        anobii = Site(
            name='Anobii',
            url='http://www.anobii.com/%s/books',
            match_type='css',
            match_expr='h1.person_heading',
            test_username_pos='bob'
        )
        session.add(anobii)

        ask_fm = Site(
            name='Ask FM',
            url='http://ask.fm/%s',
            status_code=200,
            test_username_pos='tipsofschool'
        )
        session.add(ask_fm)

        audioboom = Site(
            name='Audioboom',
            url='http://audioboom.com/%s',
            status_code=200,
            test_username_pos='bob'
        )
        session.add(audioboom)

        authorstream = Site(
            name='Authorstream',
            url='http://www.authorstream.com/%s/',
            status_code=200,
            test_username_pos='tiikmconferences'
        )
        session.add(authorstream)

        badoo = Site(
            name='Badoo',
            url='http://badoo.com/%s/',
            status_code=200,
            test_username_pos='dave'
        )
        session.add(badoo)

        behance = Site(
            name='Behance',
            url='https://www.behance.net/%s',
            status_code=200,
            test_username_pos='juste'
        )
        session.add(behance)

        bitbucket = Site(
            name='Bitbucket',
            url='https://bitbucket.org/%s',
            status_code=200,
            test_username_pos='jespern'
        )
        session.add(bitbucket)

        blip_fm = Site(
            name='Blip FM',
            url='http://blip.fm/%s',
            status_code=200,
            test_username_pos='mark_till'
        )
        session.add(blip_fm)

        blogmarks = Site(
            name='Blogmarks',
            url='http://blogmarks.net/user/%s',
            match_type='css',
            match_expr='div#infos-user',
            test_username_pos='Krome'
        )
        session.add(blogmarks)

        blogspot = Site(
            name='Blogspot',
            url='http://%s.blogspot.co.uk',
            status_code=200,
            test_username_pos='takingroot-jr'
        )
        session.add(blogspot)

        bodybuilding = Site(
            name='Bodybuilding',
            url='http://bodyspace.bodybuilding.com/%s/',
            match_type='css',
            match_expr='div.BodyBanner',
            test_username_pos='Scarfdaddy'
        )
        session.add(bodybuilding)

        break_com = Site(
            name='Break',
            url='http://www.break.com/user/%s',
            match_type='css',
            match_expr='section.profile-head',
            test_username_pos='jenny'
        )
        session.add(break_com)

        cafemom = Site(
            name='Cafemom',
            url='http://www.cafemom.com/home/%s',
            match_type='css',
            match_expr='div#member-info',
            test_username_pos='jane'
        )
        session.add(cafemom)

        car_domain = Site(
            name='Car Domain',
            url='http://www.cardomain.com/member/%s/',
            status_code=200,
            test_username_pos='dan'
        )
        session.add(car_domain)

        codeplex = Site(
            name='Codeplex',
            url='http://www.codeplex.com/site/users/view/%s',
            match_type='css',
            match_expr='h1.user_name',
            test_username_pos='dan'
        )
        session.add(codeplex)

        colour_lovers = Site(
            name='Colour Lovers',
            url='http://www.colourlovers.com/lover/%s',
            match_type='css',
            match_expr='div.column-container',
            test_username_pos='bob'
        )
        session.add(colour_lovers)

        conferize = Site(
            name='Conferize',
            url='https://www.conferize.com/u/%s/',
            match_type='css',
            match_expr='div.hero--user',
            test_username_pos='dan'
        )
        session.add(conferize)

        copy_taste = Site(
            name='Copytaste',
            url='http://copytaste.com/profile/%s',
            status_code=200,
            test_username_pos='metegulec'
        )
        session.add(copy_taste)

        cruisemates = Site(
            name='Cruisemates',
            url='http://www.cruisemates.com/forum/members/%s.html',
            match_type='css',
            match_expr='div#main_userinfo',
            test_username_pos='trip'
        )
        session.add(cruisemates)

        daily_motion = Site(
            name='Dailymotion',
            url='http://www.dailymotion.com/%s',
            status_code=200,
            test_username_pos='fanreviews'
        )
        session.add(daily_motion)

        delicious = Site(
            name='Delicious',
            url='https://del.icio.us/%s',
            status_code=200,
            test_username_pos='john'
        )
        session.add(delicious)

        deviant_art = Site(
            name='DeviantArt',
            url='http://%s.deviantart.com/',
            status_code=200,
            test_username_pos='marydoodles'
        )
        session.add(deviant_art)

        diigo = Site(
            name='Diigo',
            url='https://www.diigo.com/profile/%s',
            match_type='css',
            match_expr='div#avatarSection',
            test_username_pos='hunter53'
        )
        session.add(diigo)

        disqus = Site(
            name='Disqus',
            url='https://disqus.com/by/%s/',
            status_code=200,
            test_username_pos='willwillibe'
        )
        session.add(disqus)

        diy = Site(
            name='DIY',
            url='https://diy.org/%s',
            status_code=200,
            test_username_pos='bob'
        )
        session.add(diy)

        dribble = Site(
            name='Dribble',
            url='https://www.dribbble.com/%s',
            status_code=200,
            test_username_pos='kirp'
        )
        session.add(dribble)

        ebay = Site(
            name='Ebay',
            url='http://www.ebay.com/usr/%s',
            match_type='css',
            match_expr='div#user_image',
            test_username_pos='max'
        )
        session.add(ebay)

        etsy = Site(
            name='Etsy',
            url='https://www.etsy.com/people/%s',
            status_code=200,
            test_username_pos='betsy'
        )
        session.add(etsy)

        families = Site(
            name='Families',
            url='http://www.families.com/author/%s',
            match_type='css',
            match_expr='div#author-description',
            test_username_pos='JenThorpe'
        )
        session.add(families)

        fanpop = Site(
            name='Fanpop',
            url='http://www.fanpop.com/fans/%s',
            match_type='css',
            match_expr='div.user-header',
            test_username_pos='dan'
        )
        session.add(fanpop)

        ffffound = Site(
            name='FFFFound',
            url='http://ffffound.com/home/%s/found/',
            status_code=200,
            test_username_pos='tobbz'
        )
        session.add(ffffound)

        flavours = Site(
            name='Flavours',
            url='http://%s.flavors.me',
            status_code=200,
            test_username_pos='john'
        )
        session.add(flavours)

        flickr = Site(
            name='Flickr',
            url='https://www.flickr.com/photos/%s/',
            status_code=200,
            test_username_pos='adam'
        )
        session.add(flickr)

        foodspotting = Site(
            name='Foodspotting',
            url='http://www.foodspotting.com/%s',
            status_code=200,
            test_username_pos='dylan',
            # This site handles names with leading numerics strangely, so we
            # need to force an alphabetic negative case.
            test_username_neg='asdfqwerasdfqwer'
        )
        session.add(foodspotting)

        fotolog = Site(
            name='Fotolog',
            url='http://www.fotolog.com/%s/',
            status_code=200,
            test_username_pos='anna'
        )
        session.add(fotolog)

        foursquare = Site(
            name='Foursquare',
            url='https://foursquare.com/%s',
            status_code=200,
            test_username_pos='john'
        )
        session.add(foursquare)

        freesound = Site(
            name='Freesound',
            url='http://www.freesound.org/people/%s/',
            status_code=200,
            test_username_pos='john'
        )
        session.add(freesound)

        friend_finder_x = Site(
            name='FriendFinder-X',
            url='http://www.friendfinder-x.com/profile/%s',
            match_type='css',
            match_expr='div#tmpl_member_profile_header',
            test_username_pos='daniel'
        )
        session.add(friend_finder_x)

        funny_or_die = Site(
            name='Funny or Die',
            url='http://www.funnyordie.com/%s',
            status_code=200,
            test_username_pos='bob'
        )
        session.add(funny_or_die)

        get_it_on = Site(
            name='GETitOn',
            url='http://getiton.com/profile/%s',
            match_type='css',
            match_expr='div#profile_page_wrapper',
            test_username_pos='chris'
        )
        session.add(get_it_on)

        github = Site(
            name='Github',
            url='https://github.com/%s',
            status_code=200,
            test_username_pos='google'
        )
        session.add(github)

        godtube = Site(
            name='GodTube',
            url='http://www.godtube.com/%s/',
            status_code=200,
            test_username_pos='bball1989'
        )
        session.add(godtube)

        gogobot = Site(
            name='Gogobot',
            url='http://www.gogobot.com/user/%s',
            status_code=200,
            test_username_pos='dan'
        )
        session.add(gogobot)

        goodreads = Site(
            name='Goodreads',
            url='http://www.goodreads.com/%s',
            status_code=200,
            test_username_pos='seal'
        )
        session.add(goodreads)

        gravatar = Site(
            name='Gravatar',
            url='http://en.gravatar.com/profiles/%s',
            status_code=200,
            test_username_pos='simon'
        )
        session.add(gravatar)

        hubpages = Site(
            name='Hubpages',
            url='http://%s.hubpages.com/',
            status_code=200,
            test_username_pos='bob'
        )
        session.add(hubpages)

        i_am_pregnant = Site(
            name='i-am-pregnant',
            url='http://www.i-am-pregnant.com/members/%s/',
            status_code=200,
            test_username_pos='shiv77'
        )
        session.add(i_am_pregnant)

        if_this_then_that = Site(
            name='IFTTT',
            url='https://ifttt.com/p/%s/shared',
            status_code=200,
            test_username_pos='bsaren'
        )
        session.add(if_this_then_that)

        image_shack = Site(
            name='ImageShack',
            url='https://imageshack.com/user/%s',
            match_type='css',
            match_expr='header.user-profile',
            test_username_pos='Nicholas230'
        )
        session.add(image_shack)

        imgur = Site(
            name='Imgur',
            url='http://imgur.com/user/%s',
            status_code=200,
            test_username_pos='ThatPervert'
        )
        session.add(imgur)

        instagram = Site(
            name='Instagram',
            url='https://www.instagram.com/%s/',
            status_code=200,
            test_username_pos='kensingtonroyal'
        )
        session.add(instagram)

        instructables = Site(
            name='Instructables',
            url='http://www.instructables.com/member/%s/',
            status_code=200,
            test_username_pos='shags_j'
        )
        session.add(instructables)

        interpals = Site(
            name='InterPals',
            url='https://www.interpals.net/%s',
            match_type='css',
            match_expr='div.profile',
            test_username_pos='Seven89'
        )
        session.add(interpals)

        keybase = Site(
            name='Keybase',
            url='https://keybase.io/%s',
            status_code=200,
            test_username_pos='mehaase'
        )
        session.add(keybase)

        kongregate = Site(
            name='Kongregate',
            url='http://www.kongregate.com/accounts/%s',
            status_code=200,
            test_username_pos='Truestrike'
        )
        session.add(kongregate)

        lanyrd = Site(
            name='Lanyrd',
            url='http://lanyrd.com/profile/%s/',
            status_code=200,
            test_username_pos='shanselman'
        )
        session.add(lanyrd)

        last_fm = Site(
            name='Last.fm',
            url='http://www.last.fm/user/%s',
            status_code=200,
            test_username_pos='FrancaesG'
        )
        session.add(last_fm)

        law_of_attraction = Site(
            name='Law of Attraction',
            url='http://www.lawofattractionsingles.com/%s',
            match_type='css',
            match_expr='div.prof_top_block',
            test_username_pos='Jenniferlynnmaui'
        )
        session.add(law_of_attraction)

        library_thing = Site(
            name='LibraryThing',
            url='https://www.librarything.com/profile/%s',
            match_type='css',
            match_expr='div.profile',
            test_username_pos='Medievalgirl'
        )
        session.add(library_thing)

        lifeboat = Site(
            name='Lifeboat',
            url='https://oc.tc/%s',
            status_code=200,
            test_username_pos='Matilaina'
        )
        session.add(lifeboat)

        linked_in = Site(
            name='LinkedIn',
            url='https://www.linkedin.com/in/%s',
            status_code=200,
            test_username_pos='markhaase'
        )
        session.add(linked_in)

        marketing_land = Site(
            name='Marketing Land',
            url='http://marketingland.com/author/%s',
            status_code=200,
            test_username_pos='barb-palser'
        )
        session.add(marketing_land)

        mate1 = Site(
            name='Mate1.com',
            url='http://www.mate1.com/profiles/%s',
            status_code=200,
            test_username_pos='janedoe'
        )
        session.add(mate1)

        medium = Site(
            name='Medium',
            url='https://medium.com/@%s',
            status_code=200,
            test_username_pos='erinshawstreet'
        )
        session.add(medium)

        meetzur = Site(
            name='Meetzur',
            url='http://www.meetzur.com/%s',
            match_type='css',
            match_expr='div.profile-left',
            test_username_pos='sachin99'
        )
        session.add(meetzur)

        mixcloud = Site(
            name='Mixcloud',
            url='https://www.mixcloud.com/%s/',
            status_code=200,
            test_username_pos='dublab'
        )
        session.add(mixcloud)

        # This site was out of service at the time I tried testing it, so I
        # could not test this criteria.
        mixcrate = Site(
            name='Mixcrate',
            url='http://www.mixcrate.com/%s',
            status_code=200,
            test_username_pos='kennyrock'
        )
        session.add(mixcrate)

        mixlr = Site(
            name='Mixlr',
            url='http://mixlr.com/%s/',
            status_code=200,
            test_username_pos='therwandan'
        )
        session.add(mixlr)

        mod_db = Site(
            name='Mod DB',
            url='http://www.moddb.com/members/%s',
            status_code=200,
            test_username_pos='hugebot'
        )
        session.add(mod_db)

        muck_rack = Site(
            name='Muck Rack',
            url='https://muckrack.com/%s',
            status_code=200,
            test_username_pos='scottkleinberg'
        )
        session.add(muck_rack)

        mybuilder_com = Site(
            name='MyBuilder.com',
            url='https://www.mybuilder.com/profile/view/%s',
            status_code=200,
            test_username_pos='kdbuildingservices'
        )
        session.add(mybuilder_com)

        mylot = Site(
            name='myLot',
            url='http://www.mylot.com/%s',
            status_code=200,
            test_username_pos='LovingMyBabies'
        )
        session.add(mylot)

        myspace = Site(
            name='Myspace',
            url='https://myspace.com/%s',
            status_code=200,
            test_username_pos='kesha'
        )
        session.add(myspace)

        netvibes = Site(
            name='Netvibes',
            url='http://www.netvibes.com/%s',
            status_code=200,
            test_username_pos='grade3kis'
        )
        session.add(netvibes)

        # OKCupid
        okcupid = Site(
            name='OkCupid',
            url='https://www.okcupid.com/profile/%s',
            status_code=200,
            match_type='xpath',
            match_expr="//div[contains(@class, 'info-username')]",
            test_username_pos='the_ferett'
        )
        session.add(okcupid)

        pandora = Site(
            name='Pandora',
            url='https://www.pandora.com/profile/%s',
            match_type='css',
            match_expr='div#user_info_container',
            test_username_pos='mehaase'
        )
        session.add(pandora)

        photoblog = Site(
            name='PhotoBlog',
            url='https://www.photoblog.com/%s',
            status_code=200,
            test_username_pos='canon6d'
        )
        session.add(photoblog)

        photobucket = Site(
            name='Photobucker',
            url='http://photobucket.com/user/%s/library/',
            status_code=200,
            test_username_pos='darkgladir'
        )
        session.add(photobucket)

        picture_trail = Site(
            name='PictureTrail',
            url='http://www.picturetrail.com/%s',
            match_type='css',
            match_expr='td.IntroTitle-text-wt',
            test_username_pos='victoria15'
        )
        session.add(picture_trail)

        pink_bike = Site(
            name='Pinkbike',
            url='http://www.pinkbike.com/u/%s/',
            status_code=200,
            test_username_pos='mattwragg'
        )
        session.add(pink_bike)

        pinterest = Site(
            name='Pinterest',
            url='https://www.pinterest.com/%s/',
            status_code=200,
            test_username_pos='mehaase'
        )
        session.add(pinterest)

        playlists_net = Site(
            name='Playlists.Net',
            url='http://playlists.net/members/%s',
            status_code=200,
            test_username_pos='WhatisSoul'
        )
        session.add(playlists_net)

        plurk = Site(
            name='Plurk',
            url='http://www.plurk.com/%s',
            match_type='css',
            match_expr='span.nick_name',
            test_username_pos='xxSaltandPepperxx'
        )
        session.add(plurk)

        rapid7_community = Site(
            name='Rapid7 Community',
            url='https://community.rapid7.com/people/%s',
            status_code=200,
            test_username_pos='dabdine'
        )
        session.add(rapid7_community)

        # This site has banned our Splash IP so I cannot test it.
        rate_your_music = Site(
            name='Rate Your Music',
            url='http://rateyourmusic.com/~%s',
            status_code=200,
            test_username_pos='silvioporto'
        )
        session.add(rate_your_music)

        readability = Site(
            name='Readability',
            url='https://readability.com/%s/',
            status_code=200,
            test_username_pos='adam'
        )
        session.add(readability)

        reddit = Site(
            name='Reddit',
            url='https://www.reddit.com/user/%s',
            status_code=200,
            test_username_pos='mehaase'
        )
        session.add(reddit)

        scratch = Site(
            name='Scratch',
            url='https://scratch.mit.edu/users/%s/',
            status_code=200,
            test_username_pos='MeTwo'
        )
        session.add(scratch)

        setlist_fm = Site(
            name='Setlist.fm',
            url='http://www.setlist.fm/user/%s',
            status_code=200,
            test_username_pos='tw21'
        )
        session.add(setlist_fm)

        shopcade = Site(
            name='Shopcade',
            url='https://www.shopcade.com/%s',
            status_code=200,
            test_username_pos='salonidahake'
        )
        session.add(shopcade)

        # This site occasionally throws errors when testing. Maybe it doesn't
        # like having two requests so fast?
        single_muslim = Site(
            name='SingleMuslim',
            url='https://www.singlemuslim.com/searchuser/%s/abc',
            match_type='css',
            match_expr='div.userProfileView',
            test_username_pos='YoghurtTub'
        )
        session.add(single_muslim)

        slashdot = Site(
            name='Slashdot',
            url='https://slashdot.org/~%s',
            match_type='css',
            match_expr='article#user_bio',
            test_username_pos='Locke2005'
        )
        session.add(slashdot)

        slideshare = Site(
            name='SlideShare',
            url='http://www.slideshare.net/%s',
            status_code=200,
            test_username_pos='dmc500hats'
        )
        session.add(slideshare)

        smite_guru = Site(
            name='SmiteGuru',
            url='http://smite.guru/stats/xb/%s/summary',
            match_type='css',
            match_expr='div.header.panel',
            test_username_pos='WatsonV3'
        )
        session.add(smite_guru)

        smug_mug = Site(
            name='SmugMug',
            url='https://%s.smugmug.com/',
            status_code=200,
            test_username_pos='therescueddog'
        )
        session.add(smug_mug)

        smule = Site(
            name='Smule',
            url='http://www.smule.com/%s',
            status_code=200,
            test_username_pos='AbsurdJoker'
        )
        session.add(smule)

        snooth = Site(
            name='Snooth',
            url='http://www.snooth.com/profiles/%s/',
            match_type='css',
            match_expr='div.profile-header',
            test_username_pos='dvogler'
        )
        session.add(snooth)

        soldier_x = Site(
            name='SoldierX',
            url='https://www.soldierx.com/hdb/%s',
            match_type='css',
            match_expr='div.field-field-hdb-photo',
            test_username_pos='achillean'
        )
        session.add(soldier_x)

        sound_cloud = Site(
            name='SoundCloud',
            url='https://soundcloud.com/%s',
            status_code=200,
            test_username_pos='youngma'
        )
        session.add(sound_cloud)

        soup = Site(
            name='Soup',
            url='http://%s.soup.io/',
            match_type='css',
            match_expr='div#userinfo',
            test_username_pos='nattaly'
        )
        session.add(soup)

        source_forge = Site(
            name='SourceForge',
            url='https://sourceforge.net/u/%s/profile/',
            status_code=200,
            test_username_pos='ronys'
        )
        session.add(source_forge)

        speaker_deck = Site(
            name='Speaker Deck',
            url='https://speakerdeck.com/%s',
            status_code=200,
            test_username_pos='rocio'
        )
        session.add(speaker_deck)

        sporcle = Site(
            name='Sporcle',
            url='http://www.sporcle.com/user/%s',
            match_type='css',
            match_expr='div#UserBox',
            test_username_pos='lolshortee'
        )
        session.add(sporcle)

        steam = Site(
            name='Steam',
            url='http://steamcommunity.com/id/%s',
            match_type='css',
            match_expr='div.profile_page',
            test_username_pos='tryh4rdz'
        )
        session.add(steam)

        stupid_cancer = Site(
            name='Stupidcancer',
            url='http://stupidcancer.org/community/profile/%s',
            status_code=200,
            test_username_pos='CatchMeYes'
        )
        session.add(stupid_cancer)

        # Tribe.net was down when I was testing. I could not verify that these
        # settings work.
        tribe = Site(
            name='Tribe',
            url='http://people.tribe.net/%s',
            status_code=200,
            test_username_pos='violetta'
        )
        session.add(tribe)

        trip_advisor = Site(
            name='TripAdvisor',
            url='https://www.tripadvisor.com/members/%s',
            status_code=200,
            test_username_pos='scrltd16'
        )
        session.add(trip_advisor)

        tumblr = Site(
            name='Tumblr',
            url='http://%s.tumblr.com/',
            status_code=200,
            test_username_pos='seanjacobcullen'
        )
        session.add(tumblr)

        twitter = Site(
            name='Twitter',
            url='https://twitter.com/%s',
            status_code=200,
            test_username_pos='mehaase'
        )
        session.add(twitter)

        untappd = Site(
            name='Untappd',
            url='https://untappd.com/user/%s',
            status_code=200,
            test_username_pos='samelawrence'
        )
        session.add(untappd)

        vimeo = Site(
            name='Vimeo',
            url='https://vimeo.com/%s',
            status_code=200,
            test_username_pos='mikeolbinski'
        )
        session.add(vimeo)

        visualize_us = Site(
            name='VisualizeUs',
            url='http://vi.sualize.us/%s/',
            status_code=200,
            test_username_pos='emilybusiness'
        )
        session.add(visualize_us)

        voices_com = Site(
            name='Voices.com',
            url='https://www.voices.com/people/%s',
            match_type='css',
            match_expr='div.voices-profile-title',
            test_username_pos='johncavanagh'
        )
        session.add(voices_com)

        wanelo = Site(
            name='Wanelo',
            url='https://wanelo.com/%s',
            status_code=200,
            test_username_pos='tsingeli'
        )
        session.add(wanelo)

        wattpad = Site(
            name='Wattpad',
            url='https://www.wattpad.com/user/%s',
            status_code=200,
            test_username_pos='Weirdly_Sarcastic'
        )
        session.add(wattpad)

        wishlistr = Site(
            name='Wishlistr',
            url='http://www.wishlistr.com/profile/%s/',
            match_type='css',
            match_expr='div#people',
            test_username_pos='seventy7'
        )
        session.add(wishlistr)

        wordpress = Site(
            name='WordPress',
            url='https://profiles.wordpress.org/%s/',
            match_type='css',
            match_expr='ul#user-meta',
            test_username_pos='sivel'
        )
        session.add(wordpress)

        xbox_gamertag = Site(
            name='Xbox Gamertag',
            url='https://www.xboxgamertag.com/search/%s/',
            status_code=200,
            test_username_pos='masterrshake'
        )
        session.add(xbox_gamertag)

        youtube = Site(
            name='YouTube',
            url='https://www.youtube.com/user/%s',
            status_code=200,
            test_username_pos='vlogdozack'
        )
        session.add(youtube)

        session.commit()

    def _create_fixture_categories(self, config):
        """
        Create default categories.
        """
        bookmarking_sites = [
            'Delicious',
            'Diigo',
            'Blogmarks'
        ]
        business_sites = [
            'Conferize',
            'Dribble',
            'Marketing Land',
            'MyBuilder.com',
            'Netvibes',
            'Voices.com',
            'WordPress',
        ]
        coding_sites = [
            'Bitbucket',
            'Codeplex',
            'Github',
            'SourceForge',
        ]
        crypto_sites = [
            'Keybase',
        ]
        dating_sites = [
            'Badoo',
            'FriendFinder-X',
            'GETitOn',
            'Law of Attraction',
            'Mate1.com',
            'OkCupid',
            'SingleMuslim',
        ]
        hobby_and_interest_sites = [
            'Anobii',
            'Authorstream',
            'Car Domain',
            'Colour Lovers',
            'DIY',
            'Goodreads',
            'Fanpop',
            'Foodspotting',
            'Kongregate',
            'Lifeboat',
            'Mod DB',
            'Muck Rack',
            'Pinkbike',
            'Readability',
            'SmiteGuru',
            'Sporcle',
            'Steam',
            'Untappd',
            'Xbox Gamertag',
        ]
        health_and_lifestyle_sites = [
            'Bodybuilding',
            'Families',
            'i-am-pregnant',
            'Stupidcancer',
        ]
        image_sites = [
            'DeviantArt',
            'FFFFound',
            'Flickr',
            'Fotolog',
            'ImageShack',
            'Imgur',
            'Photobucket',
            'Photobucker',
            'PictureTrail',
            'SmugMug',
        ]
        learning_sites = [
            'Instructables',
            'LibraryThing',
            'Speaker Deck',
            'SlideShare',
        ]
        music_sites = [
            'Audioboom',
            'Blip FM',
            'Freesound',
            'Last.fm',
            'Mixcloud',
            'Mixcrate',
            'Mixlr',
            'Mixcrate',
            'Pandora',
            'Playlists.Net',
            'Rate Your Music',
            'Setlist.fm',
            'Smule',
            'Snooth',
            'SoundCloud',

        ]
        shopping_sites = [
            'Ebay',
            'Etsy',
            'Shopcade',
        ]
        social_sites = [
            'About.me',
            'Ask FM',
            'Behance',
            'Blogspot',
            'Cafemom',
            'Copytaste',
            'Disqus',
            'Flavours',
            'Foursquare',
            'Gravatar',
            'Hubpages',
            'Instagram',
            'InterPals',
            'Lanyrd',
            'LinkedIn',
            'Medium',
            'Meetzur',
            'myLot',
            'Myspace',
            'PhotoBlog',
            'Pinterest',
            'Plurk',
            'Reddit',
            'Scratch',
            'Soup',
            'Tribe',
            'Tumblr',
            'Twitter',
            'VisualizeUs',
            'Wanelo',
            'Wattpad',
            'Wishlistr'
        ]
        technology_sites = [
            'IFTTT',
            'Rapid7 Community',
            'Slashdot',
            'SoldierX',
        ]
        travel_sites = [
            'TripAdvisor',
            'Cruisemates',
            'Gogobot',
        ]
        video_sites = [
            'Break',
            'Dailymotion',
            'Funny or Die',
            'GodTube',
            'Vimeo',
            'YouTube',
        ]

        session = app.database.get_session(self._db)

        # Bookmarking
        sites = session.query(Site) \
                       .filter(Site.name.in_(bookmarking_sites)) \
                       .all()
        bookmarking = Category(
            name='Bookmarking',
            sites=sites
        )
        session.add(bookmarking)

        # Business
        sites = session.query(Site) \
                       .filter(Site.name.in_(business_sites)) \
                       .all()
        business = Category(
            name='Business',
            sites=sites
        )
        session.add(business)

        # Coding
        sites = session.query(Site) \
                       .filter(Site.name.in_(coding_sites)) \
                       .all()
        coding = Category(
            name='Coding',
            sites=sites
        )
        session.add(coding)

        # Crypto
        sites = session.query(Site) \
                       .filter(Site.name.in_(crypto_sites)) \
                       .all()
        crypto = Category(
            name='Crypto',
            sites=sites
        )
        session.add(crypto)

        # Dating
        sites = session.query(Site) \
                       .filter(Site.name.in_(dating_sites)) \
                       .all()
        dating = Category(
            name='Dating',
            sites=sites
        )
        session.add(dating)

        # Health and Lifestyle
        sites = session.query(Site) \
                       .filter(Site.name.in_(health_and_lifestyle_sites)) \
                       .all()
        health_and_lifestyle = Category(
            name='Health and Lifestyle',
            sites=sites
        )
        session.add(health_and_lifestyle)

        # Hobby and Interest
        sites = session.query(Site) \
                       .filter(Site.name.in_(hobby_and_interest_sites)) \
                       .all()
        hobby_and_interest = Category(
            name='Hobby and Interest',
            sites=sites
        )
        session.add(hobby_and_interest)

        # Image
        sites = session.query(Site) \
                       .filter(Site.name.in_(image_sites)) \
                       .all()
        image = Category(
            name='Image',
            sites=sites
        )
        session.add(image)

        # Learning
        sites = session.query(Site) \
                       .filter(Site.name.in_(learning_sites)) \
                       .all()
        learning = Category(
            name='Learning',
            sites=sites
        )
        session.add(learning)

        # Music
        sites = session.query(Site) \
                       .filter(Site.name.in_(music_sites)) \
                       .all()
        music = Category(
            name='Music',
            sites=sites
        )
        session.add(music)

        # Shopping
        sites = session.query(Site) \
                       .filter(Site.name.in_(shopping_sites)) \
                       .all()
        shopping = Category(
            name='Shopping',
            sites=sites
        )
        session.add(shopping)

        # Social
        sites = session.query(Site) \
                       .filter(Site.name.in_(social_sites)) \
                       .all()
        social = Category(
            name='Social',
            sites=sites
        )
        session.add(social)

        # Technology
        sites = session.query(Site) \
                       .filter(Site.name.in_(technology_sites)) \
                       .all()
        technology = Category(
            name='Technology',
            sites=sites
        )
        session.add(technology)

        # Travel
        sites = session.query(Site) \
                       .filter(Site.name.in_(travel_sites)) \
                       .all()
        travel = Category(
            name='Travel',
            sites=sites
        )
        session.add(travel)

        # Video
        sites = session.query(Site) \
                       .filter(Site.name.in_(video_sites)) \
                       .all()
        video = Category(
            name='Video',
            sites=sites
        )
        session.add(video)

        session.commit()

    def _delete_data(self):
        ''' Delete files stored in the data directory. '''
        data_dir = get_path("data")
        for file_object in os.listdir(data_dir):
            file_object_path = os.path.join(data_dir, file_object)
            if os.path.isfile(file_object_path):
                os.unlink(file_object_path)
            else:
                shutil.rmtree(file_object_path)

    def _drop_all(self):
        '''
        Drop database tables, foreign keys, etc.

        Unlike SQL Alchemy's built-in drop_all() method, this one shouldn't
        punk out if the Python schema doesn't match the actual database schema
        (a common scenario while developing).

        See:
        https://bitbucket.org/zzzeek/sqlalchemy/wiki/UsageRecipes/DropEverything
        '''

        tables = list()
        all_fks = list()
        metadata = MetaData()
        inspector = reflection.Inspector.from_engine(self._db)
        session = app.database.get_session(self._db)

        for table_name in inspector.get_table_names():
            fks = list()

            for fk in inspector.get_foreign_keys(table_name):
                if not fk['name']:
                    continue
                fks.append(ForeignKeyConstraint((), (), name=fk['name']))

            tables.append(Table(table_name, metadata, *fks))
            all_fks.extend(fks)

        for fk in all_fks:
            try:
                self._db.execute(DropConstraint(fk))
            except Exception as e:
                self._logger.warn('Not able to drop FK "%s".' % fk.name)
                self._logger.debug(str(e))

        for table in tables:
            try:
                self._db.execute(DropTable(table))
            except Exception as e:
                self._logger.warn('Not able to drop table "%s".' % table.name)
                self._logger.debug(str(e))

        session.commit()

    def _get_args(self, arg_parser):
        ''' Customize arguments. '''

        arg_parser.add_argument(
            'action',
            choices=('build', 'drop'),
            help='Specify what action to take.'
        )

        arg_parser.add_argument(
            '--debug-db',
            action='store_true',
            help='Print database queries.'
        )

        arg_parser.add_argument(
            '--sample-data',
            action='store_true',
            help='Create sample data.'
        )

        arg_parser.add_argument(
            '--delete-data',
            action='store_true',
            help='Delete archive and screenshot files from data directory.'
        )

    def _run(self, args, config):
        ''' Main entry point. '''

        if args.debug_db:
            # Configure database logging.
            log_level = getattr(logging, args.verbosity.upper())

            db_logger = logging.getLogger('sqlalchemy.engine')
            db_logger.setLevel(log_level)
            db_logger.addHandler(self._log_handler)

        # Connect to database.
        database_config = dict(config.items('database'))
        self._db = app.database.get_engine(database_config, super_user=True)

        # Run build commands.
        if args.action in ('build', 'drop'):
            self._logger.info('Dropping database tables.')
            self._drop_all()

            if args.delete_data:
                self._logger.info('Deleting data.')
                self._delete_data()

        if args.action == 'build':
            self._logger.info('Running Agnostic\'s bootstrap.')
            self._agnostic_bootstrap(config)

            self._logger.info('Creating database tables.')
            Base.metadata.create_all(self._db)

            self._logger.info('Creating fixture data.')
            self._create_fixtures(config)

        if args.action == 'build' and args.sample_data:
            self._logger.info('Creating sample data.')
            self._create_samples(config)
