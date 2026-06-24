/* address: 0x0042efd0 */
/* name: CUnitAI__Unk_0042efd0 */
/* signature: void __fastcall CUnitAI__Unk_0042efd0(void * param_1) */


void __fastcall CUnitAI__Unk_0042efd0(void *param_1)

{
  char cVar1;
  char *pcVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  char *pcVar6;
  char *pcVar7;
  undefined4 *puVar8;

  *(undefined4 *)((int)param_1 + 0xe0) = 3;
  *(undefined4 *)((int)param_1 + 0xfc) = 3;
  *(undefined4 *)((int)param_1 + 0xb8) = 0;
  *(undefined4 *)((int)param_1 + 0xb4) = 0;
  *(undefined4 *)((int)param_1 + 0x34) = 0;
  *(undefined4 *)((int)param_1 + 0x38) = 0;
  *(undefined4 *)((int)param_1 + 0x2c) = 0;
  *(undefined4 *)param_1 = 0;
  pcVar2 = (char *)OID__AllocObject(0xb,0xf,s_C__dev_ONSLAUGHT2_WorldPhysicsMa_00625850,0x5e7);
  uVar3 = 0xffffffff;
  *(char **)((int)param_1 + 0x30) = pcVar2;
  pcVar6 = s_m_b_rubble_00625878;
  do {
    pcVar7 = pcVar6;
    if (uVar3 == 0) break;
    uVar3 = uVar3 - 1;
    pcVar7 = pcVar6 + 1;
    cVar1 = *pcVar6;
    pcVar6 = pcVar7;
  } while (cVar1 != '\0');
  uVar3 = ~uVar3;
  pcVar6 = pcVar7 + -uVar3;
  for (uVar4 = uVar3 >> 2; uVar4 != 0; uVar4 = uVar4 - 1) {
    *(undefined4 *)pcVar2 = *(undefined4 *)pcVar6;
    pcVar6 = pcVar6 + 4;
    pcVar2 = pcVar2 + 4;
  }
  for (uVar3 = uVar3 & 3; uVar3 != 0; uVar3 = uVar3 - 1) {
    *pcVar2 = *pcVar6;
    pcVar6 = pcVar6 + 1;
    pcVar2 = pcVar2 + 1;
  }
  *(undefined4 *)((int)param_1 + 0xc0) = 0;
  *(undefined4 *)((int)param_1 + 0xc4) = 0;
  *(undefined4 *)((int)param_1 + 200) = 0;
  *(undefined4 *)((int)param_1 + 0xd4) = 0;
  *(undefined4 *)((int)param_1 + 0xcc) = 0;
  *(undefined4 *)((int)param_1 + 0xd0) = 0;
  *(undefined4 *)((int)param_1 + 0xf4) = 0x3f800000;
  *(undefined4 *)((int)param_1 + 0xf8) = 0x3f800000;
  *(undefined4 *)((int)param_1 + 0x144) = 0;
  *(undefined4 *)((int)param_1 + 0x148) = 0x43480000;
  *(undefined4 *)((int)param_1 + 0x14c) = 0x3f800000;
  *(undefined4 *)((int)param_1 + 0x150) = 0x3d4ccccd;
  *(undefined4 *)((int)param_1 + 0x140) = 2;
  *(undefined4 *)((int)param_1 + 0x100) = 0;
  *(undefined4 *)((int)param_1 + 0x104) = 0;
  *(undefined4 *)((int)param_1 + 0x108) = 0;
  *(undefined4 *)((int)param_1 + 0x160) = 0x3f800000;
  *(undefined4 *)((int)param_1 + 0x110) = 0;
  *(undefined4 *)((int)param_1 + 0x154) = 0;
  *(undefined4 *)((int)param_1 + 0xe4) = 0;
  *(undefined4 *)((int)param_1 + 0x188) = 0x40400000;
  *(undefined4 *)((int)param_1 + 0x18c) = 0x41400000;
  *(undefined4 *)((int)param_1 + 0x158) = 0x447a0000;
  *(undefined4 *)((int)param_1 + 0x15c) = 0x40800000;
  *(undefined4 *)((int)param_1 + 0xe8) = 0xffffffff;
  *(undefined4 *)((int)param_1 + 0xec) = 0xffffffff;
  *(undefined4 *)((int)param_1 + 0xf0) = 0xffffffff;
  *(undefined4 *)((int)param_1 + 0xd8) = 0x40c90fdb;
  *(undefined4 *)((int)param_1 + 0xdc) = 0x40c90fdb;
  *(undefined4 *)((int)param_1 + 8) = 0;
  *(undefined4 *)((int)param_1 + 0xc) = 0;
  *(undefined4 *)((int)param_1 + 0x10) = 0;
  *(undefined4 *)((int)param_1 + 0x18) = 0;
  *(undefined4 *)((int)param_1 + 0x1c) = 0;
  *(undefined4 *)((int)param_1 + 0x14) = 0;
  *(undefined4 *)((int)param_1 + 4) = 0;
  *(undefined4 *)((int)param_1 + 0x20) = 0;
  *(undefined4 *)((int)param_1 + 0x24) = 0;
  *(undefined4 *)((int)param_1 + 0x28) = 0;
  *(undefined4 *)((int)param_1 + 0x118) = 0;
  *(undefined4 *)((int)param_1 + 0x11c) = 0;
  *(undefined4 *)((int)param_1 + 0x120) = 0;
  *(undefined4 *)((int)param_1 + 0x124) = 0;
  puVar8 = (undefined4 *)((int)param_1 + 0x164);
  for (iVar5 = 7; iVar5 != 0; iVar5 = iVar5 + -1) {
    *puVar8 = 0x3f800000;
    puVar8 = puVar8 + 1;
  }
  *(undefined4 *)((int)param_1 + 400) = 0;
  *(undefined4 *)((int)param_1 + 0x194) = 0;
  *(undefined4 *)((int)param_1 + 0x180) = 0;
  *(undefined4 *)((int)param_1 + 0xbc) = 0;
  *(undefined4 *)((int)param_1 + 0x184) = 0;
  *(undefined4 *)((int)param_1 + 0x10c) = 0;
  *(undefined4 *)((int)param_1 + 0x128) = 0;
  *(undefined4 *)((int)param_1 + 300) = 0;
  *(undefined4 *)((int)param_1 + 0x130) = 0;
  *(undefined4 *)((int)param_1 + 0x198) = 0;
  *(undefined4 *)((int)param_1 + 0x19c) = 0;
  *(undefined4 *)((int)param_1 + 0x134) = 0;
  *(undefined4 *)((int)param_1 + 0x138) = 0;
  *(undefined4 *)((int)param_1 + 0x13c) = 0;
  *(undefined4 *)((int)param_1 + 0x1a0) = 0;
  *(undefined4 *)((int)param_1 + 0x1a4) = 0;
  *(undefined4 *)((int)param_1 + 0x7c) = 0;
  *(undefined4 *)((int)param_1 + 0x80) = 0;
  *(undefined4 *)((int)param_1 + 0x84) = 0;
  *(undefined4 *)((int)param_1 + 0x88) = 0;
  *(undefined4 *)((int)param_1 + 0x8c) = 0;
  *(undefined4 *)((int)param_1 + 0x90) = 0;
  *(undefined4 *)((int)param_1 + 0x94) = 0;
  *(undefined4 *)((int)param_1 + 0x98) = 0;
  *(undefined4 *)((int)param_1 + 0x9c) = 0;
  *(undefined4 *)((int)param_1 + 0xa0) = 0;
  *(undefined4 *)((int)param_1 + 0xa4) = 0;
  *(undefined4 *)((int)param_1 + 0xa8) = 0;
  *(undefined4 *)((int)param_1 + 0xac) = 0;
  *(undefined4 *)((int)param_1 + 0x1a8) = 0xffffffff;
  *(undefined4 *)((int)param_1 + 0x114) = 1;
  return;
}
