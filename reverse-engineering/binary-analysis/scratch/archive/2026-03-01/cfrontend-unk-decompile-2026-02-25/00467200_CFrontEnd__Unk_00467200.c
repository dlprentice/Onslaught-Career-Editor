/* address: 0x00467200 */
/* name: CFrontEnd__Unk_00467200 */
/* signature: void __thiscall CFrontEnd__Unk_00467200(void * this, int param_1, float param_2, float param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CFrontEnd__Unk_00467200(void *this,int param_1,float param_2,float param_3)

{
  float fVar1;
  float fVar2;
  float fVar3;
  int iVar4;
  float fVar5;
  float10 fVar6;
  float10 fVar7;
  float local_14;
  int local_10;
  int local_8;

  fVar3 = param_2;
  fVar5 = 3.22299e-44;
  if (*(int *)((int)this + 0x1f8) == -1) {
    fVar5 = *(float *)((int)this + 0x200);
    if (fVar5 == param_2) {
      fVar5 = *(float *)((int)this + 0x1fc);
    }
    switch(fVar5) {
    case 9.80909e-45:
    case 1.12104e-44:
    case 1.26117e-44:
    case 1.4013e-44:
    case 1.54143e-44:
    case 1.82169e-44:
    case 1.96182e-44:
    case 2.24208e-44:
    case 2.38221e-44:
    case 2.66247e-44:
      iVar4 = CFrontEnd__Unk_004679a0((int)param_2);
      if ((iVar4 != 0) && ((int)fVar5 < (int)param_2)) {
        return;
      }
    }
  }
  if (((param_2 == 7.00649e-45) || (param_2 == 8.40779e-45)) || (param_2 == 2.10195e-44)) {
    param_2 = 1.0;
  }
  else {
    param_2 = ((float)param_1 - _DAT_005d8bc4) * _DAT_005d85bc;
    if (_DAT_005d856c <= param_2) {
      if (_DAT_005d8568 < param_2) {
        param_2 = _DAT_005d8568;
      }
    }
    else {
      param_2 = _DAT_005d856c;
    }
  }
  CUnitAI__Unk_00452fd0(param_2);
  switch(fVar3) {
  case 9.80909e-45:
  case 1.12104e-44:
  case 1.26117e-44:
  case 1.4013e-44:
  case 1.54143e-44:
  case 1.82169e-44:
  case 1.96182e-44:
  case 2.24208e-44:
  case 2.38221e-44:
  case 2.66247e-44:
    if (((fVar5 != 1.82169e-44) && (fVar5 != 2.38221e-44)) &&
       ((fVar3 != 1.82169e-44 && (fVar3 != 2.38221e-44)))) {
      param_1 = 0x3f800000;
    }
  }
  local_8 = 0xff;
  if (((fVar5 == 1.82169e-44) || (fVar5 == 2.38221e-44)) ||
     ((fVar3 == 1.82169e-44 ||
      (((fVar3 == 2.38221e-44 || (*(int *)((int)this + 0x1f8) == 0xd)) ||
       (param_2 = 1.25, *(int *)((int)this + 0x1f8) == 0x11)))))) {
    param_2 = 1.4;
  }
  local_14 = 0.0;
  if ((float)param_1 < _DAT_005d8568) {
    if (fVar3 == 0.0) {
      if ((float)param_1 < _DAT_005d8604) {
        local_8 = 0;
      }
      if (_DAT_005d85ec <= (float)param_1) {
        if ((float10)_DAT_005d8bb8 <= (float10)(float)param_1) {
          if ((float)param_1 < _DAT_005d8bec) {
            fVar1 = ((float)param_1 - _DAT_005d8bb8) * _DAT_005dbb5c;
            fVar2 = _DAT_005d856c;
            if ((_DAT_005d856c <= fVar1) && (fVar2 = fVar1, _DAT_005d8568 < fVar1)) {
              fVar2 = _DAT_005d8568;
            }
            param_2 = fVar2 * (param_2 - _DAT_005d8568) + _DAT_005d8568;
          }
        }
        else {
          param_2 = 1.0;
        }
      }
      else {
        fVar6 = ((float10)(float)param_1 - (float10)_DAT_005d8604) * (float10)_DAT_005dbb60;
        if ((float10)_DAT_005d856c <= fVar6) {
          if ((float10)_DAT_005d8568 < fVar6) {
            fVar6 = (float10)_DAT_005d8568;
          }
        }
        else {
          fVar6 = (float10)_DAT_005d856c;
        }
        local_8 = (int)(longlong)ROUND(fVar6 * (float10)_DAT_005d8c70);
        if (local_8 < 0) {
          param_2 = (float)fVar6;
          fVar6 = fVar6 * (float10)_DAT_005d8cb4;
          local_8 = 0;
        }
        else {
          if (0xff < local_8) {
            local_8 = 0xff;
          }
          param_2 = (float)fVar6;
          fVar6 = fVar6 * (float10)_DAT_005d8cb4;
        }
LAB_00467574:
        local_14 = (float)-fVar6;
      }
    }
    else {
      if (fVar5 != 1.82169e-44) {
        fVar6 = (float10)(float)param_1 - (float10)_DAT_005d85ec;
        fVar6 = fVar6 + fVar6;
        if ((float10)_DAT_005d856c <= fVar6) {
          if ((float10)_DAT_005d8568 < fVar6) {
            fVar6 = (float10)_DAT_005d8568;
          }
        }
        else {
          fVar6 = (float10)_DAT_005d856c;
        }
        fVar6 = (float10)_DAT_005d8568 - fVar6;
        local_8 = (int)(longlong)ROUND(((float10)_DAT_005d8568 - fVar6) * (float10)_DAT_005d8c70);
        if (local_8 < 0) {
          local_8 = 0;
        }
        else if (0xff < local_8) {
          local_8 = 0xff;
        }
        param_2 = (float)(fVar6 * (float10)_DAT_005db4b4 + (float10)_DAT_005db4b0);
        goto LAB_00467574;
      }
      fVar6 = (float10)fcos((float10)(float)param_1 * (float10)_DAT_005d85e8);
      fVar1 = _DAT_005d8568;
      if (fVar6 < (float10)_DAT_005d856c) {
        fVar1 = _DAT_005d8be0;
      }
      fVar2 = ABS((float)fVar6);
      if (fVar2 != _DAT_005d856c) {
        fVar2 = SQRT(fVar2);
      }
      fVar1 = fVar1 * fVar2 * _DAT_005d85ec + _DAT_005d85ec;
      param_2 = fVar1 * _DAT_005db4b0 + (_DAT_005d8568 - fVar1) * _DAT_005db4b4;
    }
  }
  fVar1 = param_2;
  fVar6 = (float10)fcos((float10)_DAT_008a9570 * (float10)_DAT_005d85fc);
  fVar7 = (float10)fsin((float10)_DAT_008a9570 * (float10)_DAT_005d85fc);
  CDXSurf__RenderSurface
            ((float)(fVar7 * (float10)_DAT_005d8be8 + (float10)_DAT_005dbb54),
             (float)(fVar6 * (float10)_DAT_005d8cc0 + (float10)_DAT_005dbb58),0x3eb33333,
             DAT_0089d8dc,(local_8 * 0x3f & 0xff00U) << 0x10,param_2 * _DAT_005db4ac,
             param_2 * _DAT_005db4ac,4,0,0x3f800000,local_14);
  CDXSurf__RenderSurface
            (0x43a40000,0x43ab8000,0x3e4ccccd,DAT_0089d8dc,
             ~(local_8 * 0xff0000) & 0xffffffU ^ local_8 * 0xff0000,param_2,param_2,4,0,0x3f800000,
             local_14);
  local_10 = 0xff;
  local_14 = 0.0;
  if ((_DAT_005d8568 <= (float)param_1) || (fVar3 != 0.0)) goto LAB_00467846;
  if (_DAT_005d85ec <= (float)param_1) {
    if (_DAT_005d8bec <= (float)param_1) {
      if (_DAT_005d8bb0 <= (float)param_1) goto LAB_00467846;
      fVar2 = ((float)param_1 - _DAT_005d8bec) * _DAT_005db4b8;
      fVar3 = _DAT_005d856c;
      if ((_DAT_005d856c <= fVar2) && (fVar3 = fVar2, _DAT_005d8568 < fVar2)) {
        fVar3 = _DAT_005d8568;
      }
      param_2 = _DAT_005d8568 - fVar3;
      local_10 = (int)(longlong)ROUND(param_2 * _DAT_005d8c70);
      if (-1 < local_10) goto joined_r0x00467774;
      local_10 = 0;
      goto LAB_0046777b;
    }
    param_2 = 1.0;
  }
  else {
    fVar3 = ((float)param_1 - _DAT_005d8604) * _DAT_005dbb60;
    param_2 = _DAT_005d856c;
    if ((_DAT_005d856c <= fVar3) && (param_2 = fVar3, _DAT_005d8568 < fVar3)) {
      param_2 = _DAT_005d8568;
    }
    local_10 = (int)(longlong)ROUND(param_2 * _DAT_005d8c70);
    if (local_10 < 0) {
      local_10 = 0;
    }
    else {
joined_r0x00467774:
      if (0xff < local_10) {
        local_10 = 0xff;
      }
    }
LAB_0046777b:
    local_14 = -(param_2 * _DAT_005d8cb4);
  }
  fVar6 = (float10)fcos((float10)_DAT_008a9570 * (float10)_DAT_005d85fc);
  fVar7 = (float10)fsin((float10)_DAT_008a9570 * (float10)_DAT_005d85fc);
  CDXSurf__RenderSurface
            ((float)(fVar7 * (float10)_DAT_005d8be8 + (float10)_DAT_005dbb54),
             (float)(fVar6 * (float10)_DAT_005d8cc0 + (float10)_DAT_005dbb58),0x3eb33333,
             DAT_0089d8e0,(local_10 * 0x3f & 0xff00U) << 0x10,param_2 * _DAT_005db4ac,
             param_2 * _DAT_005db4ac,4,0,0x3f800000,local_14);
  CDXSurf__RenderSurface
            (0x43a40000,0x43ab8000,0x3e4ccccd,DAT_0089d8e0,
             ~(local_10 * 0xff0000) & 0xffffffU ^ local_10 * 0xff0000,param_2,param_2,4,0,0x3f800000
             ,local_14);
LAB_00467846:
  if (((_DAT_005d8bc4 < (float)param_1) || (fVar5 == 1.82169e-44)) || (fVar5 == 2.38221e-44)) {
    RenderState_Set(0x13,1);
    RenderState_Set(0x14,2);
    D3DStateCache__SetState114Raw(0,1,3);
    D3DStateCache__SetState114Raw(0,2,3);
    CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
    CDXSurf__RenderSurface
              (0x43a40000,0x43ab8000,0x3dcccccd,DAT_0089d8e4,0xffffffff,fVar1,fVar1,4,0,0x3f800000,0
              );
    CDXSurf__RenderSurface
              (0x41200000,0x43700000,0x3dcccccd,DAT_0089d834,0xffffffff,0x40000000,0x41700000,4,0,
               0x3f800000,0);
    RenderState_Set(0x13,5);
    RenderState_Set(0x14,6);
    D3DStateCache__SetState114Raw(0,1,1);
    D3DStateCache__SetState114Raw(0,2,1);
    CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
  }
  return;
}
