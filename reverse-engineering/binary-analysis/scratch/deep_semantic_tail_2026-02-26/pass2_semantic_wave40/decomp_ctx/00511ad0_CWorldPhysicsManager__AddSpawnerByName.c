/* address: 0x00511ad0 */
/* name: CWorldPhysicsManager__AddSpawnerByName */
/* signature: undefined CWorldPhysicsManager__AddSpawnerByName(void) */


void __thiscall
CWorldPhysicsManager__AddSpawnerByName(int param_1,byte *param_2,void *param_3,int param_4)

{
  byte bVar1;
  int *piVar2;
  int *item;
  byte *pbVar3;
  int iVar4;
  byte *pbVar5;
  int iVar6;
  bool bVar7;

  item = (int *)OID__AllocObject(0xc,4,s_C__dev_ONSLAUGHT2_WorldPhysicsMa_0063d798,0x2e6);
  if (param_2 != (byte *)0x0) {
    iVar6 = 0;
    piVar2 = (int *)*DAT_008553f4;
    DAT_008553f4[2] = (int)piVar2;
    if (piVar2 == (int *)0x0) {
      iVar4 = 0;
    }
    else {
      iVar4 = *piVar2;
    }
    while (iVar4 != 0) {
      pbVar5 = *(byte **)(iVar4 + 8);
      pbVar3 = param_2;
      do {
        bVar1 = *pbVar3;
        bVar7 = bVar1 < *pbVar5;
        if (bVar1 != *pbVar5) {
LAB_00511b3f:
          iVar4 = (1 - (uint)bVar7) - (uint)(bVar7 != 0);
          goto LAB_00511b44;
        }
        if (bVar1 == 0) break;
        bVar1 = pbVar3[1];
        bVar7 = bVar1 < pbVar5[1];
        if (bVar1 != pbVar5[1]) goto LAB_00511b3f;
        pbVar3 = pbVar3 + 2;
        pbVar5 = pbVar5 + 2;
      } while (bVar1 != 0);
      iVar4 = 0;
LAB_00511b44:
      if (iVar4 == 0) goto LAB_00511b69;
      iVar6 = iVar6 + 1;
      piVar2 = *(int **)(DAT_008553f4[2] + 4);
      DAT_008553f4[2] = (int)piVar2;
      if (piVar2 == (int *)0x0) {
        iVar4 = 0;
      }
      else {
        iVar4 = *piVar2;
      }
    }
  }
  iVar6 = -1;
LAB_00511b69:
  *item = iVar6;
  item[1] = param_4;
  iVar6 = CWorldPhysicsManager__Unk_005115b0(param_3);
  item[2] = iVar6;
  if (*item == -1) {
    CConsole__Printf(&DAT_0066f580,s_Spawner___s__not_found_0063dafc);
  }
  CSPtrSet__AddToTail((void *)(param_1 + 0x4c),item);
  return;
}
