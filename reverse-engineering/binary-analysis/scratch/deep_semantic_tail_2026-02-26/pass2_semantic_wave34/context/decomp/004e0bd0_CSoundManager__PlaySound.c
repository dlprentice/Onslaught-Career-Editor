/* address: 0x004e0bd0 */
/* name: CSoundManager__PlaySound */
/* signature: undefined CSoundManager__PlaySound(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void * __thiscall
CSoundManager__PlaySound
          (void *param_1,void *param_2,undefined4 param_3,undefined4 param_4,undefined4 param_5,
          float param_6,undefined4 param_7,undefined4 param_8,undefined1 param_9,undefined4 param_10
          ,uint param_11,byte param_12,undefined4 param_13)

{
  float fVar1;
  float fVar2;
  float fVar3;
  void *this;
  int iVar4;
  float10 fVar5;
  unkbyte10 Var6;
  int iVar7;
  int local_10;

  CGame__GetCamera(&DAT_008a9a98,0);
  if ((param_2 == (void *)0x0) || (param_12 != 0)) {
    iVar7 = 1;
  }
  else {
    iVar7 = 0;
  }
  this = (void *)CSoundManager__AllocateSoundEvent(param_1,iVar7);
  if (this != (void *)0x0) {
    CGenericActiveReader__SetReader(this,param_2);
    *(undefined4 *)((int)this + 0x1c) = param_5;
    *(undefined4 *)((int)this + 0xc) = param_3;
    *(undefined4 *)((int)this + 0x2c) = 0;
    iVar7 = CSoundManager__FindFreeChannel(&DAT_00896988);
    *(int *)((int)this + 4) = iVar7;
    *(undefined1 *)((int)this + 0x18) = param_9;
    *(undefined4 *)((int)this + 0x3c) = param_10;
    *(undefined4 *)((int)this + 0x38) = param_10;
    *(uint *)((int)this + 0x7c) = param_11 & 0xff;
    *(undefined4 *)((int)this + 0x40) = 0;
    *(uint *)((int)this + 0x80) = (uint)param_12;
    *(undefined4 *)((int)this + 0x84) = 0;
    *(undefined4 *)((int)this + 0x14) = param_13;
    *(undefined1 *)((int)this + 8) = 1;
    if (param_2 == (void *)0x0) {
      *(undefined4 *)((int)this + 0x10) = 0;
    }
    else {
      *(undefined4 *)((int)this + 0x10) = param_4;
    }
    if (param_6 == _DAT_005d856c) {
      *(undefined4 *)((int)this + 0x24) = 0;
      *(undefined4 *)((int)this + 0x20) = 0x3f800000;
    }
    else if (_DAT_005d856c <= param_6) {
      *(undefined4 *)((int)this + 0x20) = 0;
      *(float *)((int)this + 0x24) = param_6;
      *(undefined4 *)((int)this + 0x28) = 0x3f800000;
    }
    else {
      *(undefined4 *)((int)this + 0x20) = 0x3f800000;
      *(float *)((int)this + 0x24) = param_6;
      *(undefined4 *)((int)this + 0x28) = 0;
    }
    *(undefined4 *)((int)this + 0x30) = param_7;
    *(undefined4 *)((int)this + 0x6c) = param_8;
    if ((param_2 == (void *)0x0) || (param_12 != 0)) {
      *(undefined4 *)((int)this + 0x34) = 0;
    }
    else {
      Var6 = fpatan((float10)*(float *)((int)this + 0x44),(float10)*(float *)((int)this + 0x48));
      fVar5 = (float10)fsin(Var6);
      fVar1 = _DAT_005d8be0;
      if ((float10)_DAT_005d856c < fVar5) {
        fVar1 = _DAT_005d8568;
      }
      fVar2 = (float)fVar5 * _DAT_005d85cc * (float)fVar5 * _DAT_005d85cc;
      local_10 = (int)(longlong)ROUND(fVar2 * fVar2 * fVar1);
      *(int *)((int)this + 0x34) = local_10;
    }
    CSoundManager__Unk_004e1360(this,1);
    fVar1 = *(float *)((int)this + 0x44);
    fVar2 = *(float *)((int)this + 0x48);
    fVar3 = *(float *)((int)this + 0x4c);
    CGame__GetCamera(&DAT_008a9a98,0);
    fVar1 = SQRT(-fVar1 * -fVar1 + -fVar2 * -fVar2 + -fVar3 * -fVar3);
    fVar2 = _DAT_005d85d0 - fVar1;
    fVar3 = _DAT_005d85d0;
    if ((fVar2 <= _DAT_005d85d0) && (fVar3 = fVar2, fVar2 < _DAT_005d856c)) {
      fVar3 = _DAT_005d856c;
    }
    local_10 = (int)(longlong)ROUND(fVar3 * _DAT_005db020 * _DAT_005d8cc8);
    _param_9 = local_10;
    if ((_DAT_005d85d0 <= fVar1) && (*(char *)((int)this + 0x18) == '\0')) {
      if (*(int *)((int)this + 0x74) != 0) {
        *(undefined4 *)(*(int *)((int)this + 0x74) + 0x78) = *(undefined4 *)((int)this + 0x78);
      }
      if (*(int *)((int)this + 0x78) == 0) {
        *(undefined4 *)((int)param_1 + 0xc) = *(undefined4 *)((int)this + 0x74);
      }
      else {
        *(undefined4 *)(*(int *)((int)this + 0x78) + 0x74) = *(undefined4 *)((int)this + 0x74);
      }
      *(int *)((int)param_1 + 8) = *(int *)((int)param_1 + 8) + -1;
      *(undefined4 *)((int)this + 0x74) = *(undefined4 *)((int)param_1 + 0x34);
      *(undefined4 *)((int)this + 0x78) = 0;
      if (*(int *)((int)param_1 + 0x34) != 0) {
        *(void **)(*(int *)((int)param_1 + 0x34) + 0x78) = this;
      }
      *(void **)((int)param_1 + 0x34) = this;
      return (void *)0x0;
    }
    if (*(int *)((int)this + 0x10) == 0) {
      _param_9 = 0x7f;
    }
    fVar1 = *(float *)((int)this + 0x20) * *(float *)((int)this + 0x1c);
    if (*(int *)((int)this + 0x14) == 1) {
      local_10 = (int)(longlong)
                      ROUND(fVar1 * *(float *)((int)param_1 + 0x24) *
                            *(float *)((int)param_1 + 0x20) * _DAT_005dbc4c);
    }
    else {
      local_10 = (int)(longlong)
                      ROUND(fVar1 * *(float *)((int)param_1 + 0x28) *
                            *(float *)((int)param_1 + 0x20) * _DAT_005dbc4c);
    }
    local_10 = local_10 * 200;
    if (10000 < local_10) {
      local_10 = 10000;
    }
    iVar7 = (local_10 + -10000) / 2;
    if (iVar7 < -10000) {
      iVar7 = -10000;
    }
    if (*(int *)((int)this + 0x14) == 1) {
      local_10 = (int)(longlong)
                      ROUND((float)_param_9 * *(float *)((int)param_1 + 0x24) * fVar1 *
                            *(float *)((int)param_1 + 0x20));
    }
    else {
      local_10 = (int)(longlong)
                      ROUND((float)_param_9 * *(float *)((int)param_1 + 0x28) * fVar1 *
                            *(float *)((int)param_1 + 0x20));
    }
    local_10 = local_10 * 200;
    if (10000 < local_10) {
      local_10 = 10000;
    }
    iVar4 = (local_10 + -10000) / 2;
    if (iVar4 < -10000) {
      iVar4 = -10000;
    }
    *(int *)((int)this + 0x68) = iVar4;
    *(int *)((int)this + 100) = iVar7;
    if (-1 < *(int *)((int)this + 4)) {
      CSoundManager__PlaySoundOnChannel(&DAT_00896988,this);
    }
  }
  return this;
}
