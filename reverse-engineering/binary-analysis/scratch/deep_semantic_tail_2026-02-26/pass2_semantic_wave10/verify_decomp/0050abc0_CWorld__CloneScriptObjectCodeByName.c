/* address: 0x0050abc0 */
/* name: CWorld__CloneScriptObjectCodeByName */
/* signature: int __thiscall CWorld__CloneScriptObjectCodeByName(void * this, int param_1, void * param_2) */


int __thiscall CWorld__CloneScriptObjectCodeByName(void *this,int param_1,void *param_2)

{
  byte bVar1;
  byte *pbVar2;
  int iVar3;
  undefined4 *puVar4;
  byte *pbVar5;
  bool bVar6;

  puVar4 = *(undefined4 **)((int)this + 0x120);
  *(undefined4 **)((int)this + 0x128) = puVar4;
  if (puVar4 == (undefined4 *)0x0) {
    puVar4 = (undefined4 *)0x0;
  }
  else {
    puVar4 = (undefined4 *)*puVar4;
  }
  do {
    if (puVar4 == (undefined4 *)0x0) {
      CConsole__Printf(&DAT_0066f580,s_FATAL_ERROR__Cant_find_script____0063d288);
      return 0;
    }
    pbVar2 = (byte *)(**(code **)(*(int *)*puVar4 + 0x38))();
    pbVar5 = (byte *)param_1;
    do {
      bVar1 = *pbVar2;
      bVar6 = bVar1 < *pbVar5;
      if (bVar1 != *pbVar5) {
LAB_0050ac13:
        iVar3 = (1 - (uint)bVar6) - (uint)(bVar6 != 0);
        goto LAB_0050ac18;
      }
      if (bVar1 == 0) break;
      bVar1 = pbVar2[1];
      bVar6 = bVar1 < pbVar5[1];
      if (bVar1 != pbVar5[1]) goto LAB_0050ac13;
      pbVar2 = pbVar2 + 2;
      pbVar5 = pbVar5 + 2;
    } while (bVar1 != 0);
    iVar3 = 0;
LAB_0050ac18:
    if (iVar3 == 0) {
      iVar3 = CScriptObjectCode__Clone();
      return iVar3;
    }
    puVar4 = *(undefined4 **)(*(int *)((int)this + 0x128) + 4);
    *(undefined4 **)((int)this + 0x128) = puVar4;
    if (puVar4 == (undefined4 *)0x0) {
      puVar4 = (undefined4 *)0x0;
    }
    else {
      puVar4 = (undefined4 *)*puVar4;
    }
  } while( true );
}
