/* address: 0x004d2c10 */
/* name: CPlayer__GotoPanView */
/* signature: void __thiscall CPlayer__GotoPanView(void * this, float for_time) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* Player.cpp mapping correction: this is GotoPanView(float), not ApplyForce. Resets pan state,
   allocates/initializes monitor list + vectors/BSpline, constructs CPanCamera, and schedules
   control-view transition (event code 4000). */

void __thiscall CPlayer__GotoPanView(void *this,float for_time)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  void *pvVar5;
  float *pfVar6;
  void *this_00;
  int iVar7;
  float *pfVar8;
  float local_3c [4];
  float local_2c;
  float local_28;
  float local_24;
  float local_1c;
  float local_18;
  float local_14;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d47eb;
  local_c = ExceptionList;
  if (*(int *)((int)this + 0x1c) == 0) {
    return;
  }
  ExceptionList = &local_c;
  *(undefined4 *)((int)this + 0x24) = 0;
  pvVar5 = (void *)OID__AllocObject(0x10,0x28,s_C__dev_ONSLAUGHT2_Player_cpp_00631690,0xa0);
  local_4 = 0;
  if (pvVar5 == (void *)0x0) {
    pvVar5 = (void *)0x0;
  }
  else {
    CSPtrSet__Init(pvVar5);
  }
  local_4 = 0xffffffff;
  if (pvVar5 == (void *)0x0) {
    ExceptionList = local_c;
    return;
  }
  pfVar6 = (float *)(*(int *)((int)this + 0x1c) + 0x3c);
  pfVar8 = local_3c;
  for (iVar7 = 0xc; iVar7 != 0; iVar7 = iVar7 + -1) {
    *pfVar8 = *pfVar6;
    pfVar6 = pfVar6 + 1;
    pfVar8 = pfVar8 + 1;
  }
  if (((((DAT_008a9d38 == 0xe7) || (DAT_008a9d38 == 0xe8)) || (DAT_008a9d38 == 0x14b)) ||
      ((DAT_008a9d38 == 0xdd || (DAT_008a9d38 == 0xde)))) ||
     ((DAT_008a9d38 == 0x20c || ((DAT_008a9d38 == 0x20b || (DAT_008a9d38 == 0x14c)))))) {
    pfVar6 = (float *)OID__AllocObject(0x10,0x26,s_C__dev_ONSLAUGHT2_Player_cpp_00631690,0xb1);
    if (pfVar6 != (float *)0x0) {
      local_1c = local_1c * _DAT_005d85d8;
      local_2c = local_2c * _DAT_005d85d8;
      *pfVar6 = local_3c[0] * _DAT_005d85d8;
      pfVar6[1] = local_2c;
      pfVar6[2] = local_1c;
      goto LAB_004d2e24;
    }
  }
  else {
    pfVar6 = (float *)OID__AllocObject(0x10,0x26,s_C__dev_ONSLAUGHT2_Player_cpp_00631690,0xb5);
    if (pfVar6 == (float *)0x0) {
      pfVar6 = (float *)0x0;
    }
    else {
      fVar1 = local_18 * _DAT_005d85cc;
      fVar2 = local_14 * _DAT_005de794;
      fVar3 = local_28 * _DAT_005d85cc;
      fVar4 = local_24 * _DAT_005de794;
      *pfVar6 = local_3c[2] * _DAT_005de794 + local_3c[1] * _DAT_005d85cc;
      pfVar6[1] = fVar4 + fVar3;
      pfVar6[2] = fVar2 + fVar1;
    }
    CSPtrSet__AddToTail(pvVar5,pfVar6);
    pfVar6 = (float *)OID__AllocObject(0x10,0x26,s_C__dev_ONSLAUGHT2_Player_cpp_00631690,0xb6);
    if (pfVar6 != (float *)0x0) {
      local_1c = local_1c * _DAT_005d85d8;
      fVar1 = local_14 * _DAT_005dbbf8;
      local_2c = local_2c * _DAT_005d85d8;
      fVar2 = local_24 * _DAT_005dbbf8;
      *pfVar6 = local_3c[0] * _DAT_005d85d8 + local_3c[2] * _DAT_005dbbf8;
      pfVar6[1] = fVar2 + local_2c;
      pfVar6[2] = fVar1 + local_1c;
      goto LAB_004d2e24;
    }
  }
  pfVar6 = (float *)0x0;
LAB_004d2e24:
  CSPtrSet__AddToTail(pvVar5,pfVar6);
  pfVar6 = (float *)OID__AllocObject(0x10,0x26,s_C__dev_ONSLAUGHT2_Player_cpp_00631690,0xb9);
  if (pfVar6 == (float *)0x0) {
    pfVar6 = (float *)0x0;
  }
  else {
    fVar1 = local_18 * _DAT_005de790;
    local_14 = local_14 * _DAT_005de78c;
    fVar2 = local_28 * _DAT_005de790;
    local_24 = local_24 * _DAT_005de78c;
    *pfVar6 = local_3c[2] * _DAT_005de78c + local_3c[1] * _DAT_005de790;
    pfVar6[1] = local_24 + fVar2;
    pfVar6[2] = local_14 + fVar1;
  }
  CSPtrSet__AddToTail(pvVar5,pfVar6);
  pfVar6 = (float *)OID__AllocObject(0x10,0x26,s_C__dev_ONSLAUGHT2_Player_cpp_00631690,0xba);
  if (pfVar6 == (float *)0x0) {
    pfVar6 = (float *)0x0;
  }
  else {
    local_18 = local_18 * _DAT_005de788;
    local_28 = local_28 * _DAT_005de788;
    *pfVar6 = local_3c[1] * _DAT_005de788;
    pfVar6[1] = local_28;
    pfVar6[2] = local_18;
  }
  CSPtrSet__AddToTail(pvVar5,pfVar6);
  iVar7 = OID__AllocObject(0x14,0x28,s_C__dev_ONSLAUGHT2_Player_cpp_00631690,0xbc);
  local_4 = 1;
  if (iVar7 == 0) {
    pvVar5 = (void *)0x0;
  }
  else {
    pvVar5 = (void *)CBSpline__ctor(pvVar5,3);
  }
  local_4 = 0xffffffff;
  this_00 = (void *)OID__AllocObject(0x9c,0x26,s_C__dev_ONSLAUGHT2_Player_cpp_00631690,0xbe);
  local_4 = 2;
  if (this_00 == (void *)0x0) {
    pvVar5 = (void *)0x0;
  }
  else {
    pvVar5 = CPanCamera__ctor(this_00,*(void **)((int)this + 0x1c),pvVar5,for_time);
  }
  local_4 = 0xffffffff;
  CGame__SetCurrentCamera(&DAT_008a9a98,*(int *)((int)this + 0x2c) + -1,pvVar5,'\x01');
  if (_DAT_005d856c < for_time) {
    for_time = for_time - _DAT_005d8578;
  }
  CEventManager__AddEvent_TimeFromNow(&EVENT_MANAGER,&for_time,4000,this,0,(void *)0x0,(void *)0x0);
  ExceptionList = local_c;
  return;
}
