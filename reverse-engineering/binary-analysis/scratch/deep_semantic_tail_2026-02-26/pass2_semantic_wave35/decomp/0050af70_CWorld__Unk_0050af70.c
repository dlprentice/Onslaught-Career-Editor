/* address: 0x0050af70 */
/* name: CWorld__Unk_0050af70 */
/* signature: int * __thiscall CWorld__Unk_0050af70(void * this, int param_1, void * param_2) */


int * __thiscall CWorld__Unk_0050af70(void *this,int param_1,void *param_2)

{
  byte bVar1;
  undefined4 *puVar2;
  byte *pbVar3;
  int iVar4;
  int *piVar5;
  byte *pbVar6;
  bool bVar7;

  puVar2 = *(undefined4 **)((int)this + 0xa0);
  *(undefined4 **)((int)this + 0xa8) = puVar2;
  if (puVar2 == (undefined4 *)0x0) {
    piVar5 = (int *)0x0;
  }
  else {
    piVar5 = (int *)*puVar2;
  }
  do {
    if (piVar5 == (int *)0x0) {
      return (int *)0x0;
    }
    pbVar3 = (byte *)(**(code **)(*piVar5 + 0xa4))();
    pbVar6 = (byte *)param_1;
    do {
      bVar1 = *pbVar6;
      bVar7 = bVar1 < *pbVar3;
      if (bVar1 != *pbVar3) {
LAB_0050afc8:
        iVar4 = (1 - (uint)bVar7) - (uint)(bVar7 != 0);
        goto LAB_0050afcd;
      }
      if (bVar1 == 0) break;
      bVar1 = pbVar6[1];
      bVar7 = bVar1 < pbVar3[1];
      if (bVar1 != pbVar3[1]) goto LAB_0050afc8;
      pbVar6 = pbVar6 + 2;
      pbVar3 = pbVar3 + 2;
    } while (bVar1 != 0);
    iVar4 = 0;
LAB_0050afcd:
    if (iVar4 == 0) {
      return piVar5;
    }
    puVar2 = *(undefined4 **)(*(int *)((int)this + 0xa8) + 4);
    *(undefined4 **)((int)this + 0xa8) = puVar2;
    if (puVar2 == (undefined4 *)0x0) {
      piVar5 = (int *)0x0;
    }
    else {
      piVar5 = (int *)*puVar2;
    }
  } while( true );
}
