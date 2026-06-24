/* address: 0x0052cd20 */
/* name: CD3DApplication__Helper_0052cd20 */
/* signature: double __stdcall CD3DApplication__Helper_0052cd20(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double CD3DApplication__Helper_0052cd20(int param_1)

{
  int iVar1;
  double dVar2;
  double dVar3;
  longlong lVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  uint uVar8;
  undefined4 uVar9;
  undefined4 uVar10;
  uint uVar11;
  bool bVar12;
  longlong lVar13;
  LARGE_INTEGER local_8;

  if (DAT_0089c2bc == 0) {
    DAT_0089c2bc = 1;
    DAT_0089c2c0 = QueryPerformanceFrequency(&local_8);
    if (DAT_0089c2c0 != 0) {
      DAT_0089c2c8 = local_8.s.LowPart;
      DAT_0089c2cc = local_8.s.HighPart;
      goto LAB_0052cd6c;
    }
  }
  else {
LAB_0052cd6c:
    if (DAT_0089c2c0 != 0) {
      if (((DAT_0089c2d0 == 0 && DAT_0089c2d4 == 0) || (param_1 == 1)) || (param_1 == 4)) {
        QueryPerformanceCounter(&local_8);
        uVar9 = local_8.s.HighPart;
        uVar10 = local_8.s.LowPart;
      }
      else {
        local_8.s.HighPart = DAT_0089c2d4;
        local_8.s.LowPart = DAT_0089c2d0;
        uVar9 = DAT_0089c2d4;
        uVar10 = DAT_0089c2d0;
      }
      uVar5 = DAT_0089c2d0;
      lVar4 = CONCAT44(DAT_0089c2d4,DAT_0089c2d0);
      if (param_1 == 6) {
        bVar12 = (uint)uVar10 < DAT_0089c2d8;
        local_8.s.LowPart = uVar10 - DAT_0089c2d8;
        DAT_0089c2d8 = uVar10;
        local_8.s.HighPart = (uVar9 - DAT_0089c2dc) - (uint)bVar12;
        DAT_0089c2dc = uVar9;
        return (double)(longlong)local_8 / (double)CONCAT44(DAT_0089c2cc,DAT_0089c2c8);
      }
      if (param_1 == 5) {
        local_8.s.HighPart = (uVar9 - DAT_0089c2e4) - (uint)((uint)uVar10 < DAT_0089c2e0);
        local_8.s.LowPart = uVar10 - DAT_0089c2e0;
        return (double)(longlong)local_8 / (double)CONCAT44(DAT_0089c2cc,DAT_0089c2c8);
      }
      uVar6 = DAT_0089c2d0;
      iVar7 = DAT_0089c2d4;
      uVar8 = uVar10;
      iVar1 = uVar9;
      if (param_1 == 0) {
LAB_0052ce43:
        DAT_0089c2e4 = iVar1;
        DAT_0089c2e0 = uVar8;
        DAT_0089c2d4 = iVar7;
        DAT_0089c2d0 = uVar6;
        DAT_0089c2d8 = uVar10;
        DAT_0089c2dc = uVar9;
        return (double)_DAT_005d856c;
      }
      if (param_1 == 1) {
        DAT_0089c2d0 = 0;
        uVar11 = uVar10 - uVar5;
        iVar1 = uVar9 - DAT_0089c2d4;
        DAT_0089c2d4 = 0;
        uVar6 = DAT_0089c2d0;
        iVar7 = DAT_0089c2d4;
        uVar8 = DAT_0089c2e0 + uVar11;
        iVar1 = DAT_0089c2e4 + (iVar1 - (uint)((uint)uVar10 < uVar5)) +
                (uint)CARRY4(DAT_0089c2e0,uVar11);
        goto LAB_0052ce43;
      }
      uVar6 = uVar10;
      iVar7 = uVar9;
      uVar8 = DAT_0089c2e0;
      iVar1 = DAT_0089c2e4;
      if (param_1 == 2) goto LAB_0052ce43;
      if (param_1 == 3) {
        lVar13 = __alldiv(DAT_0089c2c8,DAT_0089c2cc,10,0);
        lVar13 = lVar13 + lVar4;
        DAT_0089c2d0 = (int)lVar13;
        DAT_0089c2d4 = (int)((ulonglong)lVar13 >> 0x20);
        return (double)_DAT_005d856c;
      }
      if (param_1 == 4) {
        return (double)(longlong)local_8 / (double)CONCAT44(DAT_0089c2cc,DAT_0089c2c8);
      }
      goto LAB_0052d02d;
    }
  }
  if (((_DAT_0089c2f8 == _DAT_005d87b0) || (param_1 == 1)) || (dVar2 = _DAT_0089c2f8, param_1 == 4))
  {
    local_8.s.LowPart = timeGetTime();
    local_8.s.HighPart = 0;
    dVar2 = (double)(longlong)local_8 * _DAT_005d8bc8;
  }
  if (param_1 == 6) {
    dVar3 = dVar2 - _DAT_0089c2e8;
    _DAT_0089c2e8 = dVar2;
    return dVar3;
  }
  if (param_1 == 5) {
    return dVar2 - _DAT_0089c2f0;
  }
  if (param_1 == 0) {
    _DAT_0089c2f0 = dVar2;
    _DAT_0089c2e8 = dVar2;
    return (double)_DAT_005d856c;
  }
  if (param_1 == 1) {
    dVar3 = dVar2 - _DAT_0089c2f8;
    _DAT_0089c2f8 = 0.0;
    _DAT_0089c2f0 = dVar3 + _DAT_0089c2f0;
    _DAT_0089c2e8 = dVar2;
    return (double)_DAT_005d856c;
  }
  if (param_1 == 2) {
    _DAT_0089c2f8 = dVar2;
    return (double)_DAT_005d856c;
  }
  if (param_1 == 3) {
    _DAT_0089c2f8 = _DAT_0089c2f8 + _DAT_005d8c38;
    return (double)_DAT_005d856c;
  }
  if (param_1 == 4) {
    return dVar2;
  }
LAB_0052d02d:
  return (double)_DAT_005d8be0;
}
