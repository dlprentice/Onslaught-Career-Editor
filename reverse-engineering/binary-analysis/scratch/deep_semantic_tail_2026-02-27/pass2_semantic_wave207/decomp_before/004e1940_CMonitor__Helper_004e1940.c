/* address: 0x004e1940 */
/* name: CMonitor__Helper_004e1940 */
/* signature: void __thiscall CMonitor__Helper_004e1940(void * this, void * param_1, void * param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CMonitor__Helper_004e1940(void *this,void *param_1,void *param_2)

{
  uchar uVar1;
  void *pvVar2;
  int iVar3;
  int iVar4;

  if ((*(char *)((int)this + 4) != '\0') && (param_1 != (void *)0x0)) {
    iVar4 = 0;
    pvVar2 = param_1;
    do {
      pvVar2 = *(void **)((int)pvVar2 + 0xd4);
      iVar4 = iVar4 + 1;
    } while (pvVar2 != (void *)0x0);
    iVar3 = _rand();
    for (iVar3 = iVar3 % iVar4; iVar3 != 0; iVar3 = iVar3 + -1) {
      param_1 = *(void **)((int)param_1 + 0xd4);
    }
    if ((*(int *)((int)param_1 + 200) != 0) &&
       (uVar1 = CSoundManager__GetOutputEnabledFlag(), uVar1 != '\0')) {
      _rand();
    }
    DAT_0083cfa0 = *(undefined1 *)((int)param_1 + 0xcc);
    if (*(char *)((int)this + 4) == '\0') {
      CConsole__Printf(&DAT_0066f580,s_ERROR__Could_not_play_sample___s_006322f0);
      DAT_0083cfa0 = 0;
      return;
    }
    iVar4 = CSoundManager__GetOrCreateSample(this,(char *)((int)param_1 + 0x40),0,'\0');
    if (iVar4 != 0) {
      CSoundManager__PlaySample();
      DAT_0083cfa0 = 0;
      return;
    }
    CConsole__Printf(&DAT_0066f580,s_ERROR__PlayNamedSample_failed_to_006322b8);
    DAT_0083cfa0 = 0;
  }
  return;
}
