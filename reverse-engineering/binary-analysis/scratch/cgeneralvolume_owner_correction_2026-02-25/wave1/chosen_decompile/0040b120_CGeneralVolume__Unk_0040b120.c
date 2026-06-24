/* address: 0x0040b120 */
/* name: CGeneralVolume__Unk_0040b120 */
/* signature: void __fastcall CGeneralVolume__Unk_0040b120(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CGeneralVolume__Unk_0040b120(void *param_1)

{
  float fVar1;
  int *this;
  int iVar2;
  float *pfVar3;
  float unaff_EBX;
  float unaff_ESI;
  void *unaff_EDI;
  float10 extraout_ST0;
  float10 extraout_ST0_00;
  float10 fVar4;
  double dVar5;
  float fVar6;
  undefined1 auStack_70 [12];
  float fStack_64;
  float fStack_60;
  float fStack_5c;
  float fStack_4c;
  float fStack_48;
  float fStack_44;
  float fStack_40;
  undefined1 auStack_34 [28];
  undefined1 auStack_18 [8];
  undefined1 auStack_10 [16];

  iVar2 = (**(code **)(*(int *)param_1 + 0x1d4))();
  fVar1 = *(float *)((int)param_1 + 0x114);
  *(undefined4 *)((int)param_1 + 0x50c) = *(undefined4 *)((int)param_1 + 0x504);
  this = *(int **)((int)param_1 + 0x4e0);
  *(undefined4 *)((int)param_1 + 0x508) = *(undefined4 *)((int)param_1 + 0x500);
  if (this == (int *)0x0) {
    *(undefined4 *)((int)param_1 + 0x4e4) = 0;
    *(undefined4 *)((int)param_1 + 0x4f0) = 0;
  }
  else {
    if ((*(byte *)(this + 0xd) & 0x10) == 0) {
      CThing__Unk_004f3ac0(this,(int)auStack_70,unaff_EDI);
    }
    else {
      (**(code **)(*this + 0x168))(auStack_70);
    }
    if ((*(int *)(iVar2 + 0xa0) == 0) || (*(int *)(*(int *)(iVar2 + 0xa0) + 0xb0) == 0)) {
      (**(code **)(*(int *)param_1 + 0x6c))(auStack_10);
      Vec3__SetXYZ();
      Vec3__SetXYZ();
      fVar4 = (float10)fpatan((float10)fStack_44,(float10)fStack_40);
      fVar4 = -fVar4;
      if ((_DAT_005d85c8 <= unaff_EBX) || (fVar4 <= (float10)_DAT_005d85e4)) {
        if ((_DAT_005d85e4 < unaff_EBX) && (fVar4 < (float10)_DAT_005d85c8)) {
          fVar4 = fVar4 + (float10)_DAT_005d85e0;
        }
      }
      else {
        fVar4 = fVar4 - (float10)_DAT_005d85e0;
      }
      *(float *)((int)param_1 + 0x4e4) = (float)-((float10)unaff_EBX - fVar4);
      dVar5 = SQRT__Wrapper_004026b0(&fStack_44);
      if (dVar5 <= (double)_DAT_005d856c) {
        fVar6 = 0.0;
      }
      else {
        CDXTexture__Unk_0055dcb0();
        fVar6 = (float)extraout_ST0_00;
      }
      dVar5 = CGeneralVolume__Unk_0040b660(fVar1,fVar6);
      *(float *)((int)param_1 + 0x4f0) = -(float)dVar5;
    }
    else {
      pfVar3 = (float *)(**(code **)(*(int *)param_1 + 0x6c))(auStack_10);
      fStack_64 = *pfVar3 + *(float *)((int)param_1 + 0x1c);
      fStack_60 = pfVar3[1] + *(float *)((int)param_1 + 0x20);
      fStack_5c = pfVar3[2] + *(float *)((int)param_1 + 0x24);
      Vec3__SetXYZ();
      (**(code **)(**(int **)((int)param_1 + 0x4e0) + 0x6c))(auStack_34);
      Vec3__SetXYZ();
      Vec3__SetXYZ();
      Vec3__SetXYZ();
      (**(code **)(*(int *)param_1 + 0x6c))(auStack_18);
      Vec3__SetXYZ();
      Vec3__SetXYZ();
      fVar4 = (float10)fpatan((float10)fStack_4c,(float10)fStack_48);
      fVar4 = -fVar4;
      if ((_DAT_005d85c8 <= (float)unaff_EDI) || (fVar4 <= (float10)_DAT_005d85e4)) {
        if ((_DAT_005d85e4 < (float)unaff_EDI) && (fVar4 < (float10)_DAT_005d85c8)) {
          fVar4 = fVar4 + (float10)_DAT_005d85e0;
        }
      }
      else {
        fVar4 = fVar4 - (float10)_DAT_005d85e0;
      }
      *(float *)((int)param_1 + 0x4e4) = (float)-((float10)(float)unaff_EDI - fVar4);
      dVar5 = SQRT__Wrapper_004026b0(&fStack_4c);
      if (dVar5 <= (double)_DAT_005d856c) {
        fVar4 = (float10)_DAT_005d856c;
      }
      else {
        CDXTexture__Unk_0055dcb0();
        fVar4 = extraout_ST0;
      }
      fVar1 = (float)fVar4;
      if ((_DAT_005d85c8 <= unaff_ESI) || (fVar1 <= _DAT_005d85e4)) {
        if ((_DAT_005d85e4 < unaff_ESI) && (fVar1 < _DAT_005d85c8)) {
          fVar4 = (float10)fVar1 + (float10)_DAT_005d85e0;
        }
      }
      else {
        fVar4 = (float10)fVar1 - (float10)_DAT_005d85e0;
      }
      fVar4 = -((float10)unaff_ESI - fVar4);
      *(float *)((int)param_1 + 0x4f0) = (float)fVar4;
      if ((float10)_DAT_005d8604 < ABS((float10)*(float *)((int)param_1 + 0x4e4)) + ABS(fVar4)) {
        *(undefined4 *)((int)param_1 + 0x500) = *(undefined4 *)((int)param_1 + 0x4e4);
        *(float *)((int)param_1 + 0x504) = (float)fVar4;
        if (*(int *)((int)param_1 + 0x4fc) == 0) {
          *(undefined4 *)((int)param_1 + 0x508) = *(undefined4 *)((int)param_1 + 0x4e4);
          *(float *)((int)param_1 + 0x50c) = (float)fVar4;
        }
        *(undefined4 *)((int)param_1 + 0x4fc) = 1;
        *(undefined4 *)((int)param_1 + 0x4e4) = 0;
        *(undefined4 *)((int)param_1 + 0x4f0) = 0;
        goto LAB_0040b5f7;
      }
    }
  }
  *(undefined4 *)((int)param_1 + 0x4fc) = 0;
LAB_0040b5f7:
  *(undefined4 *)((int)param_1 + 0x4ec) = *(undefined4 *)((int)param_1 + 0x4e8);
  *(undefined4 *)((int)param_1 + 0x4f8) = *(undefined4 *)((int)param_1 + 0x4f4);
  *(float *)((int)param_1 + 0x4e8) =
       (*(float *)((int)param_1 + 0x4e4) - *(float *)((int)param_1 + 0x4e8)) * _DAT_005d85ec +
       *(float *)((int)param_1 + 0x4e8);
  *(float *)((int)param_1 + 0x4f4) =
       (*(float *)((int)param_1 + 0x4f0) - *(float *)((int)param_1 + 0x4f4)) * _DAT_005d85ec +
       *(float *)((int)param_1 + 0x4f4);
  return;
}
