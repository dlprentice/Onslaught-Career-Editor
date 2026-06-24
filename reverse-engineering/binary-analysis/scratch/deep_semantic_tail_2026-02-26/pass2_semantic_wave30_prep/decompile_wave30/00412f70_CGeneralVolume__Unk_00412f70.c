/* address: 0x00412f70 */
/* name: CGeneralVolume__Unk_00412f70 */
/* signature: void __thiscall CGeneralVolume__Unk_00412f70(void * this, int param_1, float param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CGeneralVolume__Unk_00412f70(void *this,int param_1,float param_2)

{
  float fVar1;
  int iVar2;
  float unaff_ESI;
  float fStack_50;
  float fStack_4c;
  float fStack_48;
  float fStack_3c;
  undefined1 auStack_30 [4];
  float fStack_2c;
  float fStack_1c;
  float fStack_c;

  fVar1 = *(float *)((*(int **)((int)this + 0x20))[300] + 0x10) * _DAT_005d8cc8 * (float)param_1;
  iVar2 = (**(code **)(**(int **)((int)this + 0x20) + 0x10c))();
  if ((iVar2 != 0) && (iVar2 = *(int *)((int)this + 0x44), iVar2 < 1)) {
    if ((*(float *)((int)this + 0x40) < _DAT_006236b0) &&
       ((_DAT_006236b0 < (float)param_1 && (iVar2 == 0)))) {
      *(float *)((int)this + 0x38) = DAT_00672fd0;
    }
    if ((((*(float *)((int)this + 0x40) < _DAT_006236b4) && (_DAT_006236b4 < (float)param_1)) &&
        (iVar2 == 0)) &&
       ((DAT_00672fd0 - _DAT_006236ac < *(float *)((int)this + 0x34) &&
        (*(float *)((int)this + 0x34) < DAT_00672fd0 - _DAT_006236ac * _DAT_005d85ec)))) {
      CConsole__Printf(&DAT_0066f580,s_do_dash_Backward_00623920);
      CMonitor__Helper_004e1940
                (&DAT_00896988,*(void **)((int)*(void **)((int)this + 0x20) + 0x5b4),
                 *(void **)((int)this + 0x20));
      iVar2 = CGeneralVolume__Unk_00414030(this);
      if (iVar2 != 0) {
        *(undefined4 *)(iVar2 + 0x60) = 0;
      }
      *(undefined4 *)(*(int *)((int)this + 0x20) + 0x2ec) = 0;
      fVar1 = _DAT_006236c0 * fVar1;
      *(undefined4 *)((int)this + 0x44) = DAT_006236b8;
    }
    *(int *)((int)this + 0x40) = param_1;
    fStack_3c = -fVar1;
    CSquadNormal__Helper_004062d0
              (auStack_30,*(void **)(*(int *)((int)this + 0x20) + 0x114),0.0,0.0,unaff_ESI);
    fStack_50 = fStack_2c * fStack_3c;
    fStack_4c = fStack_1c * fStack_3c;
    fStack_48 = fStack_c * fStack_3c;
    if ((*(int **)((int)this + 0x20))[0x162] != 0) {
      fStack_50 = fStack_50 * _DAT_005d858c;
      fStack_4c = fStack_4c * _DAT_005d858c;
      fStack_48 = fStack_48 * _DAT_005d858c;
    }
    (**(code **)(**(int **)((int)this + 0x20) + 0x74))(&fStack_50);
  }
  return;
}
