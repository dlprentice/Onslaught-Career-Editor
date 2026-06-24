/* address: 0x00451930 */
/* name: CFEPBEConfig__FindEntryByName */
/* signature: int __cdecl CFEPBEConfig__FindEntryByName(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __cdecl CFEPBEConfig__FindEntryByName(void *param_1)

{
  byte bVar1;
  int iVar2;
  byte *pbVar3;
  int iVar4;
  byte *pbVar5;
  bool bVar6;

  _DAT_006602a8 = DAT_006602a0;
  if (DAT_006602a0 == (int *)0x0) {
    iVar2 = 0;
  }
  else {
    iVar2 = *DAT_006602a0;
  }
  do {
    if (iVar2 == 0) {
      return 0;
    }
    pbVar3 = *(byte **)(iVar2 + 0xa8);
    pbVar5 = param_1;
    do {
      bVar1 = *pbVar3;
      bVar6 = bVar1 < *pbVar5;
      if (bVar1 != *pbVar5) {
LAB_00451981:
        iVar4 = (1 - (uint)bVar6) - (uint)(bVar6 != 0);
        goto LAB_00451986;
      }
      if (bVar1 == 0) break;
      bVar1 = pbVar3[1];
      bVar6 = bVar1 < pbVar5[1];
      if (bVar1 != pbVar5[1]) goto LAB_00451981;
      pbVar3 = pbVar3 + 2;
      pbVar5 = pbVar5 + 2;
    } while (bVar1 != 0);
    iVar4 = 0;
LAB_00451986:
    if (iVar4 == 0) {
      _DAT_006602a8 = _DAT_006602a8;
      return iVar2;
    }
    _DAT_006602a8 = (int *)_DAT_006602a8[1];
    if (_DAT_006602a8 == (int *)0x0) {
      iVar2 = 0;
    }
    else {
      iVar2 = *_DAT_006602a8;
    }
  } while( true );
}
