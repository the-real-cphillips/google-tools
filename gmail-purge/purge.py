#!/usr/bin/env python
import argparse
import ThePurge


def validate_action_input(value):
    """
    Used to Validate the input of the `-a` parameter used 
    in the argparse setup below
    """

    if value.lower() not in [ 'archive', 'delete', 'trash' ]:
        raise argparse.ArgumentTypeError(f'[X] Invalid Value: {value}\nPlease use "archive", "delete" or "trash"')
    return value


def validate_bulk_input(value):
    if value.lower() in ['y', 'yes']:
        return True
    elif value.lower() in [ 'n', 'no' ]:
        return False
    else:
        return None


def main():
    auth = ThePurge.auth(scope=args.scope) 
    messages = ThePurge.Purge(auth)

    if args.label_name:
        label_id = messages.get_label_id(label_name=args.label_name)
        messages.gather(query=args.query, label=label_id)
    else:
        messages.gather(query=args.query)

    gather_output = messages.to_process
    data = messages.to_process

    if len(data) > 1000 and args.action.lower() != 'trash':
        check = None
        while check is None:
            bulk_input = input(f'[?] There are {len(data)} messages\n[?] Would you like to process these in bulk? (Y/N): ')
            if validate_bulk_input(bulk_input) is True:
                print("[I] Processing in Bulk")
                messages.batch_process(data, args.action.lower())
                check = True
            elif validate_bulk_input(bulk_input) is False:
                print("[I] Processing Normally")
                messages.purge(data, args.action.lower())
                check = True
            else:
                check = None
    else:
        messages.purge(data, args.action.lower())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PURGE!')

    parser.add_argument('-a', '--action',
                        dest='action',
                        type=validate_action_input,
                        action='store',
                        default=None,
                        required=True,
                        help="Choose: archive, delete, trash")
    parser.add_argument('-q', '--query',
                        dest='query',
                        action='store',
                        help="Enter your query string ie: older_than:30d, Use standard gmail queries")
    parser.add_argument('-l', '--label_name',
                        dest='label_name',
                        action='store',
                        help="label name to pass to the gather_label_id function")
    parser.add_argument('-b', '--bulk-process',
                        dest='bulk_process',
                        action='store_true',
                        default=False,
                        help="Pass this if you want to process in Bulk")
    parser.add_argument('-s', '--scope',
                        dest='scope',
                        action='store',
                        default='https://mail.google.com',
                        help="Changes the Auth Scope for the GMAIL API")

    args = parser.parse_args()

    main()
