/* address: 0x005119e0 */
/* name: CWorldPhysicsManager__AddWeaponByName */
/* signature: undefined CWorldPhysicsManager__AddWeaponByName(void) */


void __thiscall
CWorldPhysicsManager__AddWeaponByName(int param_1,byte *param_2,void *param_3,int param_4)

{
  byte bVar1;
  int *item;
  byte *pbVar2;
  int iVar3;
  undefined4 *puVar4;
  byte *pbVar5;
  int iVar6;
  bool bVar7;

  item = (int *)OID__AllocObject(0xc,4,s_C__dev_ONSLAUGHT2_WorldPhysicsMa_0063d798,0x2d4);
  if (param_2 != (byte *)0x0) {
    iVar6 = 0;
    puVar4 = (undefined4 *)*DAT_008553e8;
    DAT_008553e8[2] = puVar4;
    if (puVar4 == (undefined4 *)0x0) {
      puVar4 = (undefined4 *)0x0;
    }
    else {
      puVar4 = (undefined4 *)*puVar4;
    }
    while (puVar4 != (undefined4 *)0x0) {
      pbVar5 = (byte *)*puVar4;
      pbVar2 = param_2;
      do {
        bVar1 = *pbVar2;
        bVar7 = bVar1 < *pbVar5;
        if (bVar1 != *pbVar5) {
LAB_00511a4e:
          iVar3 = (1 - (uint)bVar7) - (uint)(bVar7 != 0);
          goto LAB_00511a53;
        }
        if (bVar1 == 0) break;
        bVar1 = pbVar2[1];
        bVar7 = bVar1 < pbVar5[1];
        if (bVar1 != pbVar5[1]) goto LAB_00511a4e;
        pbVar2 = pbVar2 + 2;
        pbVar5 = pbVar5 + 2;
      } while (bVar1 != 0);
      iVar3 = 0;
LAB_00511a53:
      if (iVar3 == 0) goto LAB_00511a78;
      iVar6 = iVar6 + 1;
      puVar4 = *(undefined4 **)(DAT_008553e8[2] + 4);
      DAT_008553e8[2] = puVar4;
      if (puVar4 == (undefined4 *)0x0) {
        puVar4 = (undefined4 *)0x0;
      }
      else {
        puVar4 = (undefined4 *)*puVar4;
      }
    }
  }
  iVar6 = -1;
LAB_00511a78:
  *item = iVar6;
  item[1] = param_4;
  iVar6 = CWorldPhysicsManager__Unk_005115b0(param_3);
  item[2] = iVar6;
  if (*item == -1) {
    CConsole__Printf(&DAT_0066f580,s_Weapon___s__not_found_0063dae4);
  }
  CSPtrSet__AddToTail((void *)(param_1 + 0x3c),item);
  return;
}
