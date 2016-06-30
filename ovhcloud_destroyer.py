#!/usr/bin/env python3
import ovh
import sys
from retrying import retry


def main(argv):
    if len(argv) == 0:
        print('Usage: {} <projectname>'.format(sys.argv[0]))
        sys.exit(1)
    c = OVHClient()
    project = argv[0]

    project_id = None
    for service_id in c.get('/cloud/project'):
        p = c.get('/cloud/project/{}'.format(service_id))
        print('Found project {} with id {}'.format(p['description'], p['project_id']))
        if p['description'] == project:
            project_id = p['project_id']
            break

    if not project_id:
        print("Couldn't find project with name {}".format(project))
        sys.exit(1)

    print('Fetching all instances')
    r = c.get('/cloud/project/{}/instance'.format(project_id))

    if len(r) == 0:
        print('Project {} has no running instances'.format(project))
        sys.exit(0)

    input('!!!WARNING - THIS WILL DESTROY ALL {} INSTANCES IN THE PROJECT {}!!!\nPress Enter to continue...'.format(
        len(r), project))

    for i in r:
        print('Requesting deletion of {}'.format(i['id']))
        c.delete('/cloud/project/{}/instance/{}'.format(project_id, i['id']))


class OVHClient(ovh.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @retry(stop_max_attempt_number=3)
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

    @retry(stop_max_attempt_number=3)
    def delete(self, *args, **kwargs):
        return super().delete(*args, **kwargs)


if __name__ == "__main__":
    main(sys.argv[1:])
