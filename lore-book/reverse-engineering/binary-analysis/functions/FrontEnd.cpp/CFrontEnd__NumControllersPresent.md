# CFrontEnd__NumControllersPresent

- Address: 0x00466990
- Status: Wave467 signature/comment hardened (headless apply/read-back/probe verified)
- Signature: `int __thiscall CFrontEnd__NumControllersPresent(void * this)`
- Source match: `references/Onslaught/FrontEnd.cpp:464` (`int CFrontEnd::NumControllersPresent()`)

## Purpose

Returns the number of available controller ports for frontend routing.

## Notes

In this retail PC build, the function returns fixed value `2` even though the broader source body counts present controllers. Runtime controller-detection behavior remains unproven.
