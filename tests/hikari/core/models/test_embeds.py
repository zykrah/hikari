#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © Nekoka.tt 2019
#
# This file is part of Hikari.
#
# Hikari is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hikari is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Hikari. If not, see <https://www.gnu.org/licenses/>.
import datetime

import pytest

from hikari.core.models import colors as _color
from hikari.core.models import embeds as _embed
from hikari.core.models import media


@pytest.fixture
def embed():
    return _embed.Embed()


@pytest.mark.model
def test_EmbedPart_delattr_sets_to_None():
    class Impl(_embed.EmbedPart):
        __slots__ = ("a", "b", "c")

        def __init__(self, a, b, c):
            super().__init__()
            self.a = a
            self.b = b
            self.c = c

    i = Impl(1, 2, 3)

    del i.a
    assert i.a is None


@pytest.mark.model
class TestEmbed:
    @pytest.mark.parametrize("slot", [s for s in _embed.Embed.__slots__])
    def test_Embed_init_sets_correct_defaults(self, slot, embed):
        attr = getattr(embed, slot)
        assert attr is None or slot == "_fields" and attr == [] or slot is "_assets_to_upload"

    @pytest.mark.parametrize(["field", "property"], [(s, s[1:]) for s in _embed.Embed.__slots__ if s.startswith("_")])
    def test_Embed_property_accessors_access_values(self, field, property, embed):
        if field == "_assets_to_upload":
            embed._assets_to_upload = {"key1": "value1", "key2": "value2"}
            assert getattr(embed, property) == {"key1", "key2"}
        else:
            sentinel = object()
            setattr(embed, field, sentinel)
            assert getattr(embed, property) is sentinel

    def test_Embed_set_footer(self, embed):
        embed.set_footer(text="foo", icon="bar")
        assert embed.footer.text == "foo"
        assert embed.footer.icon_url == "bar"

    def test_Embed_set_footer_with_file(self, embed):
        file = media.InMemoryFile("bar", "data")
        embed.set_footer(text="foo", icon=file)
        assert embed.footer.text == "foo"
        assert embed.footer.icon_url == "attachment://bar"
        assert file in embed.assets_to_upload

    def test_Embed_set_image(self, embed):
        embed.set_image(image="xxxxx")
        assert embed.image.url == "xxxxx"

    def test_Embed_set_image_with_file(self, embed):
        file = media.InMemoryFile("bar", "data")
        embed.set_image(image=file)
        assert embed.image.url == "attachment://bar"
        assert file in embed.assets_to_upload

    def test_Embed_set_thumbnail(self, embed):
        embed.set_thumbnail(image="yyyyy")
        assert embed.thumbnail.url == "yyyyy"

    def test_Embed_set_thumbnail_with_file(self, embed):
        file = media.InMemoryFile("bar", "data")
        embed.set_thumbnail(image=file)
        assert embed.thumbnail.url == "attachment://bar"
        assert file in embed.assets_to_upload

    def test_Embed_set_author(self, embed):
        embed.set_author(name="foo", url="bar", icon="baz")
        assert embed.author.name == "foo"
        assert embed.author.url == "bar"
        assert embed.author.icon_url == "baz"

    def test_Embed_set_author_with_file(self, embed):
        file = media.InMemoryFile("bar", "data")
        embed.set_author(name="foo", icon=file)
        assert embed.author.icon_url == "attachment://bar"
        assert file in embed.assets_to_upload

    def test_Embed_add_field(self, embed):
        assert embed.fields == []
        fields_to_add = [("foo", "bar", True), ("baz", "bork", False), ("eggs", "spam", True)]

        for i, (name, value, inline) in enumerate(fields_to_add, start=1):
            embed.add_field(name=name, value=value, inline=inline)
            assert len(embed.fields) == i

        for i, (name, value, inline) in enumerate(fields_to_add):
            field = embed.fields[i]
            assert field.name == name
            assert field.value == value
            assert field.inline is inline

    def test_Embed_remove_field(self, embed):
        a = _embed.EmbedField(name="foo", value="bar")
        b = _embed.EmbedField(name="baz", value="bork")
        c = _embed.EmbedField(name="qux", value="quxx")
        embed._fields = [a, b, c]

        embed.remove_field(1)
        assert embed.fields == [a, c]

    def test_Embed_colour_getter(self, embed):
        embed.color = 1234
        assert embed.colour == 1234

    def test_Embed_colour_setter(self, embed):
        embed.colour = 1234
        assert embed.color == 1234

    def test_Embed_to_dict_when_filled(self, embed):
        now = datetime.datetime.utcnow()
        color = 0x1A2B3C
        field1 = {"name": "this is field1", "value": "isn't it nice", "inline": True}
        field2 = {"name": "this is field2", "value": "embeds are kinda broken though", "inline": False}

        embed.title = "this title"
        embed.description = "this description"
        embed.url = "https://gitlab.com/nekokatt/hikari"
        embed.timestamp = now
        embed.color = _color.Color(color)
        embed.add_field(**field1)
        embed.add_field(**field2)
        embed.set_footer(icon="https://hornpub.com/logo.png", text="meals from 10am")
        embed.set_thumbnail(image="https://hornpub.com/corny-photo.png")
        embed._image = _embed.EmbedImage(url="https://hornpub.com/corny-photo.jpeg")
        embed.set_author(name="me me me")

        d = embed.to_dict()

        assert d == dict(
            title="this title",
            description="this description",
            url="https://gitlab.com/nekokatt/hikari",
            timestamp=now.replace(tzinfo=datetime.timezone.utc).isoformat(),
            color=color,
            fields=[field1, field2],
            footer=dict(text="meals from 10am", icon_url="https://hornpub.com/logo.png"),
            thumbnail=dict(url="https://hornpub.com/corny-photo.png"),
            image=dict(url="https://hornpub.com/corny-photo.jpeg"),
            author=dict(name="me me me"),
            type="rich",
        )

    def test_Embed_to_dict_when_empty(self, embed):
        assert embed.to_dict() == {"type": "rich"}

    def test_ReceivedEmbed_from_dict_when_filled(self):
        now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
        color = 0x1A2B3C
        field1 = {"name": "this is field1", "value": "isn't it nice", "inline": True}
        field2 = {"name": "this is field2", "value": "embeds are kinda broken though", "inline": False}

        embed = _embed.ReceivedEmbed.from_dict(
            dict(
                type="corn",
                title="this title",
                description="this description",
                url="https://gitlab.com/nekokatt/hikari",
                timestamp=now.replace(tzinfo=datetime.timezone.utc).isoformat(),
                color=color,
                fields=[field1, field2],
                footer=dict(text="meals from 10am", icon_url="https://hornpub.com/logo.png"),
                image=dict(
                    url="https://hornpub.com/corny-photo.png",
                    proxy_url="https://cdn.hornpub.com/corny-photo.png",
                    height=420,
                    width=45,
                ),
                thumbnail=dict(
                    url="https://hornpub.com/corny-photo.jpeg",
                    proxy_url="https://cdn.hornpub.com/corny-photo.jpeg",
                    height=9999,
                    width=1111,
                ),
                author=dict(name="me me me"),
                provider=dict(name="jobs in carpal tunnel therapy", url="hand-jobs.com"),
                video=dict(url="youchube.tom", height=69, width=96),
            )
        )

        assert embed.type == "corn"
        assert embed.title == "this title"
        assert embed.description == "this description"
        assert embed.url == "https://gitlab.com/nekokatt/hikari"
        assert embed.timestamp == now
        assert embed.color == _color.Color(color)
        assert len(embed.fields) == 2
        assert embed.fields[0] == _embed.EmbedField(name="this is field1", value="isn't it nice", inline=True)
        assert embed.fields[1] == _embed.EmbedField(
            name="this is field2", value="embeds are kinda broken though", inline=False
        )
        assert embed.footer.text == "meals from 10am"
        assert embed.footer.icon_url == "https://hornpub.com/logo.png"
        assert embed.image.url == "https://hornpub.com/corny-photo.png"
        assert embed.image.proxy_url == "https://cdn.hornpub.com/corny-photo.png"
        assert embed.image.height == 420
        assert embed.image.width == 45
        assert embed.thumbnail.url == "https://hornpub.com/corny-photo.jpeg"
        assert embed.thumbnail.proxy_url == "https://cdn.hornpub.com/corny-photo.jpeg"
        assert embed.thumbnail.width == 1111
        assert embed.thumbnail.height == 9999
        assert embed.author.name == "me me me"
        assert embed.provider.name == "jobs in carpal tunnel therapy"
        assert embed.provider.url == "hand-jobs.com"
        assert embed.video.url == "youchube.tom"
        assert embed.video.height == 69
        assert embed.video.width == 96

    def test_ReceivedEmbed_from_dict_when_empty(self):
        embed = _embed.ReceivedEmbed.from_dict(dict(type="your mother"))
        assert embed.type == "your mother"
        assert embed.title is None
        assert embed.description is None
        assert embed.url is None
        assert embed.timestamp is None
        assert embed.color is None
        assert embed.fields == []
        assert embed.footer is None
        assert embed.image is None
        assert embed.thumbnail is None
        assert embed.author is None
        assert embed.provider is None
        assert embed.video is None

    def test_title(self, embed):
        embed.title = "test"
        assert embed.title == "test"
        del embed.title
        assert embed.title is None

    def test_url(self, embed):
        embed.url = "test"
        assert embed.url == "test"
        del embed.url
        assert embed.url is None

    def test_timestamp(self, embed):
        now = datetime.datetime.now()
        embed.timestamp = now
        assert embed.timestamp == now
        del embed.timestamp
        assert embed.timestamp is None

    def test_description(self, embed):
        embed.description = "description"
        assert embed.description == "description"
        del embed.description
        assert embed.description is None

    def test_color(self, embed):
        embed.color = 69420
        assert embed.color == _color.Color(69420)
        del embed.color
        assert embed.color is None

    def test_footer_del(self, embed):
        embed._footer = object()
        del embed.footer
        assert embed._footer is None

    def test_image_del(self, embed):
        embed._image = object()
        del embed.image
        assert embed._image is None

    def test_thumbnail_del(self, embed):
        embed._thumbnail = object()
        del embed.thumbnail
        assert embed._thumbnail is None

    def test_author_del(self, embed):
        embed._author = object()
        del embed.author
        assert embed._author is None