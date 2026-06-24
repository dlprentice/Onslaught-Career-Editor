/* address: 0x00423720 */
/* name: CUnitAI__Unk_00423720 */
/* signature: void __fastcall CUnitAI__Unk_00423720(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CUnitAI__Unk_00423720(void *param_1)

{
  uint uVar1;
  float fVar2;
  BOOL BVar3;
  LARGE_INTEGER local_8;

  BVar3 = QueryPerformanceCounter(&local_8);
  if (BVar3 == 0) {
    local_8.s.LowPart = timeGetTime();
    local_8.s.HighPart = 0;
  }
  else if (local_8.s.LowPart == 0 && local_8.s.HighPart == 0) {
    do {
      QueryPerformanceCounter(&local_8);
    } while (local_8.s.LowPart == 0 && local_8.s.HighPart == 0);
  }
  uVar1 = *(uint *)((int)param_1 + 0x10);
  if ((local_8.s.LowPart != uVar1) || (local_8.s.HighPart != *(int *)((int)param_1 + 0x14))) {
    *(DWORD *)((int)param_1 + 0x20) = local_8.s.LowPart - uVar1;
    *(uint *)((int)param_1 + 0x24) =
         (local_8.s.HighPart - *(int *)((int)param_1 + 0x14)) - (uint)(local_8.s.LowPart < uVar1);
    *(undefined4 *)((int)param_1 + 0x10) = local_8.s.LowPart;
    *(undefined4 *)((int)param_1 + 0x14) = local_8.s.HighPart;
    fVar2 = *(float *)((int)param_1 + 4) * _DAT_005d8bc4 +
            (*(float *)param_1 / (float)*(longlong *)((int)param_1 + 0x20)) * _DAT_005d858c;
    *(float *)((int)param_1 + 4) = fVar2;
    if (fVar2 < _DAT_005d8568) {
      *(undefined4 *)((int)param_1 + 4) = 0x3f800000;
    }
    *(float *)((int)param_1 + 8) = _DAT_005d8568 / *(float *)((int)param_1 + 4);
  }
  return;
}
