/* address: 0x00511900 */
/* name: CWorldPhysicsManager__AddComponentByName */
/* signature: undefined CWorldPhysicsManager__AddComponentByName(void) */


void __thiscall CWorldPhysicsManager__AddComponentByName(int param_1,int param_2,byte *param_3)

{
  byte bVar1;
  int *piVar2;
  int *item;
  byte *pbVar3;
  int iVar4;
  byte *pbVar5;
  int iVar6;
  bool bVar7;

  item = (int *)OID__AllocObject(8,4,s_C__dev_ONSLAUGHT2_WorldPhysicsMa_0063d798,0x2c3);
  item[1] = param_2;
  if (param_3 != (byte *)0x0) {
    iVar6 = 0;
    piVar2 = (int *)*DAT_00855400;
    DAT_00855400[2] = (int)piVar2;
    if (piVar2 == (int *)0x0) {
      iVar4 = 0;
    }
    else {
      iVar4 = *piVar2;
    }
    while (iVar4 != 0) {
      pbVar5 = *(byte **)(iVar4 + 0xb0);
      pbVar3 = param_3;
      do {
        bVar1 = *pbVar3;
        bVar7 = bVar1 < *pbVar5;
        if (bVar1 != *pbVar5) {
LAB_00511979:
          iVar4 = (1 - (uint)bVar7) - (uint)(bVar7 != 0);
          goto LAB_0051197e;
        }
        if (bVar1 == 0) break;
        bVar1 = pbVar3[1];
        bVar7 = bVar1 < pbVar5[1];
        if (bVar1 != pbVar5[1]) goto LAB_00511979;
        pbVar3 = pbVar3 + 2;
        pbVar5 = pbVar5 + 2;
      } while (bVar1 != 0);
      iVar4 = 0;
LAB_0051197e:
      if (iVar4 == 0) goto LAB_005119a3;
      iVar6 = iVar6 + 1;
      piVar2 = *(int **)(DAT_00855400[2] + 4);
      DAT_00855400[2] = (int)piVar2;
      if (piVar2 == (int *)0x0) {
        iVar4 = 0;
      }
      else {
        iVar4 = *piVar2;
      }
    }
  }
  iVar6 = -1;
LAB_005119a3:
  *item = iVar6;
  if (iVar6 == -1) {
    CConsole__Printf(&DAT_0066f580,s_Component___s__not_found_0063dac8);
  }
  CSPtrSet__AddToTail((void *)(param_1 + 0x5c),item);
  return;
}
