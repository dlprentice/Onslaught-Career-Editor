/* address: 0x00423680 */
/* name: PCPlatform__Helper_00423680 */
/* signature: void __thiscall PCPlatform__Helper_00423680(void * this, int param_1, float param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall PCPlatform__Helper_00423680(void *this,int param_1,float param_2)

{
  float fVar1;
  BOOL BVar2;
  undefined8 uVar3;
  LARGE_INTEGER local_8;

  fVar1 = _DAT_005d8568 / (float)param_1;
  *(int *)((int)this + 4) = param_1;
  *(float *)((int)this + 8) = fVar1;
  uVar3 = __ftol();
  uVar3 = __aulldiv(*(undefined4 *)((int)this + 0x18),*(undefined4 *)((int)this + 0x1c),uVar3);
  *(undefined8 *)((int)this + 0x20) = uVar3;
  BVar2 = QueryPerformanceCounter(&local_8);
  if (BVar2 == 0) {
    local_8.s.LowPart = timeGetTime();
    local_8.s.HighPart = 0;
  }
  else if (local_8.s.LowPart == 0 && local_8.s.HighPart == 0) {
    do {
      QueryPerformanceCounter(&local_8);
    } while (local_8.s.LowPart == 0 && local_8.s.HighPart == 0);
    *(DWORD *)((int)this + 0x10) = local_8.s.LowPart;
    *(LONG *)((int)this + 0x14) = local_8.s.HighPart;
    return;
  }
  *(undefined4 *)((int)this + 0x10) = local_8.s.LowPart;
  *(undefined4 *)((int)this + 0x14) = local_8.s.HighPart;
  return;
}
