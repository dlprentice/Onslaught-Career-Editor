/* address: 0x004e1040 */
/* name: CSoundManager__SortEventList */
/* signature: void __fastcall CSoundManager__SortEventList(int param_1) */


void __fastcall CSoundManager__SortEventList(int param_1)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  void *pvVar4;
  int iVar5;

  for (iVar2 = *(int *)(param_1 + 0xc); iVar2 != 0; iVar2 = *(int *)(iVar2 + 0x74)) {
    iVar5 = *(int *)(iVar2 + 0x74);
    if ((iVar5 != 0) && (*(int *)(iVar2 + 0x68) < *(int *)(iVar5 + 0x68))) {
      if (*(int *)(iVar2 + 0x78) == 0) {
        *(int *)(param_1 + 0xc) = iVar5;
      }
      else {
        *(int *)(*(int *)(iVar2 + 0x78) + 0x74) = iVar5;
      }
      if (*(int *)(iVar5 + 0x74) != 0) {
        *(int *)(*(int *)(iVar5 + 0x74) + 0x78) = iVar2;
      }
      *(undefined4 *)(iVar2 + 0x74) = *(undefined4 *)(iVar5 + 0x74);
      *(undefined4 *)(iVar5 + 0x78) = *(undefined4 *)(iVar2 + 0x78);
      *(int *)(iVar2 + 0x78) = iVar5;
      *(int *)(iVar5 + 0x74) = iVar2;
    }
  }
  pvVar4 = *(void **)(param_1 + 0xc);
  iVar2 = 0;
  iVar5 = (int)(DAT_00896c54 * 3 + (DAT_00896c54 * 3 >> 0x1f & 3U)) >> 2;
  if (0 < iVar5) {
    do {
      if (pvVar4 == (void *)0x0) goto LAB_004e10dd;
      pvVar4 = *(void **)((int)pvVar4 + 0x74);
      iVar2 = iVar2 + 1;
    } while (iVar2 < iVar5);
  }
  for (; pvVar4 != (void *)0x0; pvVar4 = *(void **)((int)pvVar4 + 0x74)) {
    if (*(int *)((int)pvVar4 + 4) != -1) {
      CSoundManager__StopAndReleaseChannel(&DAT_00896988,pvVar4);
      *(undefined4 *)((int)pvVar4 + 4) = 0xffffffff;
    }
  }
LAB_004e10dd:
  pvVar4 = *(void **)(param_1 + 0xc);
  iVar2 = 0;
  bVar1 = true;
  if (0 < iVar5) {
    do {
      if (pvVar4 == (void *)0x0) {
        return;
      }
      if (!bVar1) {
        return;
      }
      if ((*(int *)((int)pvVar4 + 4) == -1) && (*(int *)((int)pvVar4 + 0x84) == 0)) {
        iVar3 = CSoundManager__FindFreeChannel(&DAT_00896988);
        *(int *)((int)pvVar4 + 4) = iVar3;
        if (iVar3 < 0) {
          bVar1 = false;
        }
        else {
          CSoundManager__PlaySoundOnChannel(&DAT_00896988,pvVar4);
        }
      }
      pvVar4 = *(void **)((int)pvVar4 + 0x74);
      iVar2 = iVar2 + 1;
    } while (iVar2 < iVar5);
  }
  return;
}
