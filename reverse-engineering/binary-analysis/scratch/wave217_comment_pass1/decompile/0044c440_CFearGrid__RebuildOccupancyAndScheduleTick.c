/* address: 0x0044c440 */
/* name: CFearGrid__RebuildOccupancyAndScheduleTick */
/* signature: void __thiscall CFearGrid__RebuildOccupancyAndScheduleTick(void * this) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* Rebuilds fear-grid occupancy state and schedules next update/tick flow.
   Part of AI fear/avoidance runtime refresh path. */

void __thiscall CFearGrid__RebuildOccupancyAndScheduleTick(void *this)

{
  float *pfVar1;
  int *piVar2;
  undefined4 *puVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  undefined4 *puVar8;
  int *piVar9;
  int iVar10;
  void *this_00;
  double dVar11;
  void *local_4c;
  longlong local_48;
  float local_40;
  float local_3c;
  undefined4 local_38;
  undefined4 local_34;
  float local_30;
  float local_2c;
  undefined4 local_28;
  undefined4 local_24;
  float local_20;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 local_14;
  float local_10;
  undefined4 local_c;
  undefined4 local_8;
  undefined4 local_4;

  iVar10 = 0x40;
  puVar8 = (undefined4 *)((int)this + 0x4008);
  do {
    iVar6 = 0x40;
    puVar3 = puVar8;
    do {
      puVar3[-0x1000] = 0;
      *puVar3 = 1;
      puVar3 = puVar3 + 0x40;
      iVar6 = iVar6 + -1;
    } while (iVar6 != 0);
    puVar8 = puVar8 + 1;
    iVar10 = iVar10 + -1;
  } while (iVar10 != 0);
  DAT_008550f8 = DAT_008550f0;
  local_4c = this;
  if (DAT_008550f0 == (undefined4 *)0x0) {
    this_00 = (void *)0x0;
  }
  else {
    this_00 = (void *)*DAT_008550f0;
  }
  while (this_00 != (void *)0x0) {
    if (*(int *)((int)this + 0x8008) == *(int *)((int)this_00 + 0x11c)) {
      dVar11 = CFearGrid__LookupFearWeightByArchetype(this_00);
      pfVar1 = (float *)((int)this_00 + 0x108);
      local_40 = *pfVar1;
      local_48._0_4_ = (int)(longlong)ROUND(dVar11 * (double)_DAT_005d8c4c);
      iVar6 = (int)local_48;
      local_3c = *(float *)((int)this_00 + 0x10c);
      local_38 = *(undefined4 *)((int)this_00 + 0x110);
      local_34 = *(undefined4 *)((int)this_00 + 0x114);
      local_48._0_4_ = (int)(longlong)ROUND(local_3c);
      local_30 = *pfVar1;
      iVar10 = ((int)((int)local_48 + ((int)local_48 >> 0x1f & 7U)) >> 3) - iVar6;
      local_2c = *(float *)((int)this_00 + 0x10c);
      local_28 = *(undefined4 *)((int)this_00 + 0x110);
      local_24 = *(undefined4 *)((int)this_00 + 0x114);
      local_48._0_4_ = (int)(longlong)ROUND(local_2c);
      iVar4 = (int)local_48 + ((int)local_48 >> 0x1f & 7U);
      local_20 = *pfVar1;
      local_1c = *(undefined4 *)((int)this_00 + 0x10c);
      local_18 = *(undefined4 *)((int)this_00 + 0x110);
      local_14 = *(undefined4 *)((int)this_00 + 0x114);
      local_48._0_4_ = (int)(longlong)ROUND(local_20);
      iVar5 = (int)local_48 + ((int)local_48 >> 0x1f & 7U);
      local_c = *(undefined4 *)((int)this_00 + 0x10c);
      local_10 = *pfVar1;
      local_8 = *(undefined4 *)((int)this_00 + 0x110);
      local_48 = (longlong)ROUND(local_10);
      local_4 = *(undefined4 *)((int)this_00 + 0x114);
      iVar4 = (iVar4 >> 3) + iVar6;
      iVar5 = (iVar5 >> 3) - iVar6;
      iVar6 = ((int)((int)local_48 + ((int)local_48 >> 0x1f & 7U)) >> 3) + iVar6;
      this = local_4c;
      if ((((0 < iVar10) && (iVar4 < 0x40)) && (0 < iVar5)) && (iVar6 < 0x40)) {
        for (; iVar10 <= iVar4; iVar10 = iVar10 + 1) {
          if (iVar5 <= iVar6) {
            puVar8 = (undefined4 *)((int)local_4c + (iVar5 * 0x40 + iVar10) * 4 + 8);
            iVar7 = (iVar6 - iVar5) + 1;
            do {
              *puVar8 = 1;
              puVar8 = puVar8 + 0x40;
              iVar7 = iVar7 + -1;
            } while (iVar7 != 0);
          }
        }
      }
    }
    DAT_008550f8 = (undefined4 *)DAT_008550f8[1];
    if (DAT_008550f8 == (undefined4 *)0x0) {
      this_00 = (void *)0x0;
    }
    else {
      this_00 = (void *)*DAT_008550f8;
    }
  }
  DAT_008550d8 = DAT_008550d0;
  if (DAT_008550d0 == (int *)0x0) {
    iVar10 = 0;
  }
  else {
    iVar10 = *DAT_008550d0;
  }
  while (iVar10 != 0) {
    if (((*(uint *)(iVar10 + 0x34) & 0x400) == 0) &&
       (*(int *)((int)this + 0x8008) == *(int *)(iVar10 + 0x138))) {
      local_48._0_4_ = (int)(longlong)ROUND(*(float *)(iVar10 + 0x20));
      iVar6 = (int)((int)local_48 + ((int)local_48 >> 0x1f & 7U)) >> 3;
      local_48 = (longlong)ROUND(*(float *)(iVar10 + 0x1c));
      iVar10 = iVar6 + -1;
      iVar6 = iVar6 + 1;
      iVar5 = (int)((int)local_48 + ((int)local_48 >> 0x1f & 7U)) >> 3;
      iVar4 = iVar5 + -1;
      iVar5 = iVar5 + 1;
      this = local_4c;
      if (((0 < iVar10) && ((iVar6 < 0x40 && (0 < iVar4)))) &&
         (piVar9 = DAT_008550d8, piVar2 = DAT_008550d8, iVar5 < 0x40)) {
        for (; DAT_008550d8 = piVar9, iVar10 <= iVar6; iVar10 = iVar10 + 1) {
          piVar9 = DAT_008550d8;
          DAT_008550d8 = piVar2;
          if (iVar4 <= iVar5) {
            puVar8 = (undefined4 *)((int)local_4c + (iVar4 * 0x40 + iVar10) * 4 + 0x4008);
            iVar7 = (iVar5 - iVar4) + 1;
            do {
              *puVar8 = 0;
              puVar8 = puVar8 + 0x40;
              iVar7 = iVar7 + -1;
              piVar9 = DAT_008550d8;
            } while (iVar7 != 0);
          }
          piVar2 = DAT_008550d8;
        }
      }
    }
    DAT_008550d8 = (int *)DAT_008550d8[1];
    if (DAT_008550d8 == (int *)0x0) {
      iVar10 = 0;
    }
    else {
      iVar10 = *DAT_008550d8;
    }
  }
  local_4c = (void *)(DAT_00672fd0 + _DAT_005d8568);
  CEventManager__AddEvent_AtTime
            (&EVENT_MANAGER,1000,this,(float *)&local_4c,0,(void *)0x0,(void *)0x0);
  return;
}
