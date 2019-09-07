def handler(event, context):
    print(event)

    base_page = '''
    <html>
    <h1>Hi!</h1>
    <form method="POST" action="">
        <label for="uri">Link:</label>
        <input type="text" id="link" name="link" size="40" autofocus />
        <br/>
        <br/>
        <input type="submit" value="Shorten it!" />
    </form>
    </html>
    '''

    return_value = {'statusCode': 200, 
    'body': base_page, 
    'headers':{'Content-Type': 'text/html'}}

    return return_value