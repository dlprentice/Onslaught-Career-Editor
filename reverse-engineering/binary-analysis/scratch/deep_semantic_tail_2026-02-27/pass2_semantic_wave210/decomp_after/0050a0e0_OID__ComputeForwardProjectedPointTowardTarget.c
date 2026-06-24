/* address: 0x0050a0e0 */
/* name: OID__ComputeForwardProjectedPointTowardTarget */
/* signature: void __thiscall OID__ComputeForwardProjectedPointTowardTarget(void * this, void * param_1, int param_2, void * param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
OID__ComputeForwardProjectedPointTowardTarget(void *this,void *param_1,int param_2,void *param_3)

{
  int iVar1;
  int extraout_EAX;
  void *unaff_EDI;
  undefined4 *unaff_retaddr;
  float *pfVar2;
  float fVar3;
  float fStack_88;
  float fStack_84;
  float local_80 [2];
  float fStack_78;
  float fStack_74;
  float local_70 [2];
  float fStack_68;
  float fStack_64;
  float fStack_60;
  float fStack_5c;
  undefined4 uStack_54;
  undefined4 local_50;
  undefined4 uStack_4c;
  float fStack_48;
  float fStack_44;
  float fStack_40;
  undefined1 auStack_34 [48];
  float *pfStack_4;

  if ((*(int *)((int)this + 0xa0) != 0) && (*(int *)(*(int *)((int)this + 0xa0) + 0xb0) != 0)) {
    OID__GetAttachmentOrOriginTransform(this,(int)local_80,unaff_EDI);
    pfVar2 = local_70;
    (**(code **)(*(int *)param_2 + 0x168))();
    if ((*(int *)((int)this + 0xa0) == 0) ||
       (iVar1 = *(int *)(*(int *)((int)this + 0xa0) + 0x18), iVar1 == 0)) {
      fVar3 = 0.0;
    }
    else if (*(int *)(iVar1 + 0x50) == 0) {
      fVar3 = *(float *)(iVar1 + 0x2c);
    }
    else {
      fVar3 = 1000.0;
    }
    OID__GetAttachmentOrBaseOrientationMatrix(this,(int)auStack_34,pfVar2);
    fStack_64 = fVar3 * *(float *)(extraout_EAX + 4);
    fStack_60 = fVar3 * *(float *)(extraout_EAX + 0x14);
    fStack_5c = fVar3 * *(float *)(extraout_EAX + 0x24);
    (**(code **)(*(int *)param_2 + 0x6c))(&fStack_44);
    fVar3 = (SQRT((fStack_88 - fStack_78) * (fStack_88 - fStack_78) +
                  (fStack_84 - fStack_74) * (fStack_84 - fStack_74) +
                  (local_80[0] - local_70[0]) * (local_80[0] - local_70[0])) /
            SQRT(fStack_68 * fStack_68 + fStack_60 * fStack_60 + fStack_64 * fStack_64)) *
            _DAT_005d857c;
    *pfStack_4 = fStack_48 * fVar3 + fStack_78;
    pfStack_4[1] = fStack_44 * fVar3 + fStack_74;
    pfStack_4[2] = fVar3 * fStack_40 + local_70[0];
    return;
  }
  (**(code **)(*(int *)param_2 + 0x168))(&local_50);
  *unaff_retaddr = uStack_54;
  unaff_retaddr[1] = local_50;
  unaff_retaddr[2] = uStack_4c;
  unaff_retaddr[3] = fStack_48;
  return;
}
