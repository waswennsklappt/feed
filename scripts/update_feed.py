from lxml import etree
import requests


def process_xml(feed_url):
    # Define the namespace mapping
    namespaces = {
        "atom": "http://www.w3.org/2005/Atom",
        "googleplay": "http://www.google.com/schemas/play-podcasts/1.0",
        "itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
        "media": "http://search.yahoo.com/mrss/",
        "podaccess": "https://access.acast.com/schema/1.0/",
        "acast": "https://schema.acast.com/1.0/"
    }

    # Download the XML file from the URL
    response = requests.get(feed_url)

    if response.status_code == 200:
        xml_data = response.content
        # Parse the XML with namespaces
        parser = etree.XMLParser(strip_cdata=False)
        tree = etree.HTML(xml_data, parser)

        root = tree

        # Modify 'link' element under 'channel'
        for link in root.xpath(".//channel/link"):
            link.text = "https://waswennsklappt.de"

        # Modify 'href' attribute in 'atom:link' under 'channel'
        for atom_link in root.xpath(".//channel/atom:link", namespaces=namespaces):
            atom_link.set("href", "https://feed.waswennsklappt.de/feed.xml")

        # Modify 'link' under 'channel'/'image'
        for image_link in root.xpath(".//channel/image/link"):
            image_link.text = "https://waswennsklappt.de"

        for enclosure_element in root.xpath(".//channel/item/enclosure"):
            url_attr = enclosure_element.get("url")
            if url_attr is not None:
                enclosure_element.set("url", "https://media.blubrry.com/2994638/chrt.fm/track/C481C3/" + url_attr)

        # Create and add the 'atom:link' element using the namespace
        atom_link_element = etree.Element('{%s}link' % namespaces["atom"], href="https://pubsubhubbub.appspot.com/",
                                          rel="hub")
        channel_element = root.xpath(".//channel")[0]  # Assuming there is only one 'channel' element
        channel_element.append(atom_link_element)

        # Delete a specific string over the entire XML
        string_to_remove = "<br /><hr><p style='color:grey; font-size:0.75em;'> Hosted on Acast. See <a style='color:grey;' target='_blank' rel='noopener noreferrer' href='https://acast.com/privacy'>acast.com/privacy</a> for more information.</p>"
        for elem in root.iter():
            if elem.text is not None:
                if string_to_remove in elem.text:
                    elem.text = etree.CDATA(elem.text.replace(string_to_remove, ''))

        xml_declaration = '<?xml version="1.0" encoding="utf-8"?>'

        # Serialize the modified XML back to a string
        modified_feed_xml = '\n'.join([xml_declaration, etree.tostring(root, encoding="utf-8").decode("utf-8")])

        return modified_feed_xml

    else:
        print("Failed to download XML from the URL. Status code:", response.status_code)
        return None


url = 'https://feeds.acast.com/public/shows/6504228accb27600118a65b8'
modified_xml = process_xml(url)

if modified_xml:
    print(modified_xml)
    with open("feed.xml", "w") as file:
        file.write(modified_xml)
