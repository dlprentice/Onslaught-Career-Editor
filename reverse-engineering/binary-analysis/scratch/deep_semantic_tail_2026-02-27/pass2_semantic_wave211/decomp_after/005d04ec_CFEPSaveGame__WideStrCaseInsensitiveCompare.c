/* address: 0x005d04ec */
/* name: CFEPSaveGame__WideStrCaseInsensitiveCompare */
/* signature: int __cdecl CFEPSaveGame__WideStrCaseInsensitiveCompare(void * param_1, void * param_2) */


int __cdecl CFEPSaveGame__WideStrCaseInsensitiveCompare(void *param_1,void *param_2)

{
  ushort uVar1;
  undefined2 uVar2;
  void *pvVar3;
  void *pvVar4;
  void *extraout_EAX;
  ushort *puVar5;
  undefined2 *puVar6;
  bool bVar7;
  bool bVar8;

  if (DAT_009d0998 == 0) {
    do {
      uVar1 = *(ushort *)param_1;
      pvVar3 = (void *)(uint)uVar1;
      if ((uVar1 < 0x5b) && (0x40 < uVar1)) {
        pvVar3 = (void *)((int)pvVar3 + 0x20);
      }
      uVar1 = *(ushort *)param_2;
      pvVar4 = (void *)(uint)uVar1;
      if ((uVar1 < 0x5b) && (0x40 < uVar1)) {
        pvVar4 = (void *)((int)pvVar4 + 0x20);
      }
      puVar5 = (ushort *)((int)param_1 + 2);
      param_2 = (void *)((int)param_2 + 2);
    } while (((short)pvVar3 != 0) &&
            (param_1._0_2_ = (short)pvVar4, bVar7 = (short)pvVar3 == (short)param_1,
            param_1 = puVar5, bVar7));
  }
  else {
    pvVar4 = (void *)InterlockedIncrement(&DAT_009d35f0);
    bVar7 = DAT_009d35ec == 0;
    if (!bVar7) {
      InterlockedDecrement(&DAT_009d35f0);
      CRT__LockByIndex(0x13);
      pvVar4 = extraout_EAX;
    }
    do {
      uVar2 = *(undefined2 *)param_1;
      param_1 = (void *)((int)param_1 + 2);
      pvVar3 = (void *)CFEPSaveGame__WideCharToLowerCompat
                                 (CONCAT22((short)((uint)pvVar4 >> 0x10),uVar2));
      puVar6 = (undefined2 *)((int)param_2 + 2);
      pvVar4 = (void *)CFEPSaveGame__WideCharToLowerCompat
                                 (CONCAT22((short)((uint)pvVar3 >> 0x10),*(undefined2 *)param_2));
      param_2._0_2_ = (short)pvVar3;
      if ((short)param_2 == 0) break;
      bVar8 = (short)param_2 == (short)pvVar4;
      param_2 = puVar6;
    } while (bVar8);
    if (bVar7) {
      InterlockedDecrement(&DAT_009d35f0);
    }
    else {
      CRT__UnlockByIndex(0x13);
    }
  }
  param_2 = pvVar3;
  param_1 = pvVar4;
  return ((uint)param_2 & 0xffff) - ((uint)param_1 & 0xffff);
}
