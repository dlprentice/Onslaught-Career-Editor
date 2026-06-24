/* address: 0x00511440 */
/* name: CWorldPhysicsManager__IsSpawnerThingTypeAllowedByName */
/* signature: int __cdecl CWorldPhysicsManager__IsSpawnerThingTypeAllowedByName(void * param_1) */


int __cdecl CWorldPhysicsManager__IsSpawnerThingTypeAllowedByName(void *param_1)

{
  byte bVar1;
  int *piVar2;
  byte *pbVar3;
  int iVar4;
  int iVar5;
  byte *pbVar6;
  bool bVar7;

  if (param_1 != (void *)0x0) {
    piVar2 = (int *)*DAT_008553fc;
    DAT_008553fc[2] = (int)piVar2;
    if (piVar2 == (int *)0x0) {
      iVar5 = 0;
    }
    else {
      iVar5 = *piVar2;
    }
    while (iVar5 != 0) {
      pbVar6 = *(byte **)(iVar5 + 0xb0);
      pbVar3 = param_1;
      do {
        bVar1 = *pbVar3;
        bVar7 = bVar1 < *pbVar6;
        if (bVar1 != *pbVar6) {
LAB_00511497:
          iVar4 = (1 - (uint)bVar7) - (uint)(bVar7 != 0);
          goto LAB_0051149c;
        }
        if (bVar1 == 0) break;
        bVar1 = pbVar3[1];
        bVar7 = bVar1 < pbVar6[1];
        if (bVar1 != pbVar6[1]) goto LAB_00511497;
        pbVar3 = pbVar3 + 2;
        pbVar6 = pbVar6 + 2;
      } while (bVar1 != 0);
      iVar4 = 0;
LAB_0051149c:
      if (iVar4 == 0) {
        if (iVar5 == 0) {
          return 0;
        }
        switch(*(undefined4 *)(iVar5 + 0xe0)) {
        case 0:
        case 2:
        case 3:
        case 4:
        case 7:
        case 0xb:
        case 0xd:
        case 0x11:
        case 0x13:
        case 0x14:
        case 0x15:
        case 0x17:
          return 1;
        default:
          return 0;
        }
      }
      piVar2 = *(int **)(DAT_008553fc[2] + 4);
      DAT_008553fc[2] = (int)piVar2;
      if (piVar2 == (int *)0x0) {
        iVar5 = 0;
      }
      else {
        iVar5 = *piVar2;
      }
    }
  }
  return 0;
}
