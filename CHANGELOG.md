# Changelog

All notable changes to this project will be documented in this file.
Please add a line to the unreleased section for every feature. If possible
reference the gitlab/github issue that is related to the change.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
- `#1055` Updated to orchestrator-core 0.0.20 to get the updated opentelemetry packages
- `#1061` Add FQDN and IP info of the remote address to IPAM for PNI type peerings with /31 /127 subnet with tags orchestrator, ippp and customer.
- `#1061` Added checks to prevent IP address modification for IP Peer ports
- `#882` Add IP Peer Port validation workflow
- Added IP Peer port modify workflow
- Added extra logging to the move port workflow so fails in `update_ims_circuits` can be debugged
- `#1054` Made the state storage of the move port workflow less verbose
- `#1054` Made the state storage of the move aggsp port workflow less verbose
- Fixed description update of parent subscriptions in both port move workflows
- `#1072` Enabled modify_sn8_service_port workflow for SPNL service ports
- Modified Dockerfile and helm chart for enabling Tilt deployments
- Added an extra validation on L3VPN to detect deploys with the service model that currently doesn't support re-using ports
- Added modify customer for IPS and IPBGP subscriptions
- Added modify customer for L2VPN subscriptions
- Added modify customer for lightpath subscriptions
- Fixed issue with maximum number of peerings, max is increased to 20
- `#1233` Merge IP-address lookup and IP-address reserve steps in node_create workflow

## [v8.2.1]

- Use Link1/2 in IMS name for redundant lightpath
- `#866` Add IP Peer domain model and create workflow
- Fixed IP Peer group populator
- Added IP Peer Port populator
- Added IP Peer populator
- `#877` Add IP Peer modify workflow
- Added some ❤️ to the docs
- Added modify customer for IPS and IPBGP subscriptions
- Added modify customer for lightpath subscriptions

## [v8.2.0]

- Remove legacy form code
- add change customer in modify workflow of IP Prefix product
- Added opentelemetry configuration and removed Opentracing
- Various package updates
- Minor tickets regarding naming

## [v8.1.6]

- Hotfix L2VPN and LP workflows

## [v8.1.2]

- Split code into a generic workflow orchestrator and surf specific workflows and code
- Package updates
- Ip peer group terminate
- Fixed a number of Bugs.
  - Ipv6 only IP static subscriptions
  - Ip Prefix schema validations

## [v8.0.0] - 2020-01-05

- Add link speed to NSO payload for core link
- Fix bug in subscription full text search
- Switch to fastapi
- Fix `#885` Set terminated node to RFC instead of OOS
- Refactored `#930` the endpoints to have schemas
- Refactored External API exception handling
- Renamed Database Tables
- Add firewall validation workflow
- Fix minor issues in ND firewall query
- `#898` Add IP Peer Group product and create workflow
- Add IP Peer Group populator
- Make debugger in local-dev stage of Dockerfile a variable
- Add IP Peer Port Product with create workflow `#865`

## [v7.1.5]

- Update ims api client

## [v7.1.4]

- Added environment parameter to skip NSO node in-sync validation step
- Fix Schedule
- Start subscriptions from one schedule
- FWAAS names in IMS correction.
- Set L2VPN speed correctly in FWAAS workflows
- Make compatible with FastAPI IMS
- Change user to www-data

## [v7.1.3]

- Make Firewall return as product type in the api.
- Fix Corelink validations issues

## [v7.1.2]

- Added Firewall subscriptions to api/subscriptions/product_type/IP/Customer id for Networkdashboard.
- Fixed type error in wsgi.py
- Added the Changelog file.
