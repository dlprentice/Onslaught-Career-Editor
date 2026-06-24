/* address: 0x004be1d0 */
/* name: CExplosionInitThing__Unk_004be1d0 */
/* signature: int CExplosionInitThing__Unk_004be1d0(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CExplosionInitThing__Unk_004be1d0(void)

{
  int iVar1;
  int *this;
  int iVar2;
  int iVar3;
  int iVar4;
  int extraout_EAX;
  uint uVar5;
  void *unaff_EDI;
  float fStack00000004;
  float fStack00000008;
  float fStack00000014;
  float fStack00000018;
  void *in_stack_00000024;
  int *in_stack_0000002c;
  int local_c;
  longlong local_8;

  this = in_stack_0000002c;
  local_8._0_4_ = (uint)(longlong)ROUND(fStack00000004);
  DAT_00809db8 = in_stack_00000024;
  local_c = (int)(uint)local_8 >> 1;
  fStack00000004 = (float)(longlong)ROUND(fStack00000008);
  uVar5 = (int)fStack00000004 >> 1;
  fStack00000008 = (float)((ulonglong)(longlong)ROUND(fStack00000008) >> 0x20);
  _fStack00000004 = CONCAT44(fStack00000008,uVar5);
  local_8 = (longlong)ROUND(fStack00000014);
  DAT_00809db4 = (int)(uint)local_8 >> 1;
  _fStack00000014 = (longlong)ROUND(fStack00000018);
  DAT_00809db0 = (int)fStack00000014 >> 1;
  *in_stack_0000002c = (uint)local_8;
  in_stack_0000002c[1] = (int)fStack00000014;
  in_stack_0000002c[2] = 0;
  in_stack_0000002c[3] = 0;
  iVar2 = CExplosionInitThing__Unk_004bc510
                    (in_stack_00000024,local_c,uVar5,DAT_00809db4,DAT_00809db0,(float)unaff_EDI);
  if (iVar2 == 0) {
    iVar2 = DAT_00809db0 * 2;
    iVar4 = DAT_00809db4 * 2;
    if (in_stack_0000002c[5] <= in_stack_0000002c[3]) {
      iVar1 = in_stack_0000002c[5] * 2;
      iVar3 = CPolyBucket__Helper_005491b0(in_stack_0000002c[4],iVar1);
      in_stack_0000002c[4] = iVar3;
      in_stack_0000002c[5] = iVar1;
      iVar1 = in_stack_0000002c[7];
      iVar3 = CPolyBucket__Helper_005491b0(in_stack_0000002c[6],iVar1 << 1);
      in_stack_0000002c[6] = iVar3;
      in_stack_0000002c[7] = iVar1 << 1;
    }
    *(char *)(in_stack_0000002c[4] + in_stack_0000002c[3]) = (char)(iVar4 + 1 >> 1);
    *(char *)(in_stack_0000002c[6] + in_stack_0000002c[3]) = (char)(iVar2 + 1 >> 1);
    iVar2 = in_stack_0000002c[3];
    in_stack_0000002c[2] = 1;
    in_stack_0000002c[3] = iVar2 + 1;
    return iVar2 + 1;
  }
  iVar4 = CExplosionInitThing__Helper_004bc6d0(in_stack_00000024,0x809db4,&DAT_00809db0,unaff_EDI);
  iVar2 = 0;
  if (iVar4 != 0) {
    iVar4 = CExplosionInitThing__Helper_004bc6d0
                      (in_stack_00000024,(int)&local_c,&stack0x00000004,unaff_EDI);
    iVar2 = 0;
    if (iVar4 != 0) {
      DAT_00809dbc = (int)fStack00000004;
      DAT_00829dc4 = (int)fStack00000004;
      DAT_00829dc0 = local_c;
      DAT_00829dc8 = local_c;
      DAT_00630ab4 = (int)fStack00000004 + 1;
      DAT_00630ab8 = local_c + 1;
      iVar2 = CExplosionInitThing__Helper_004be420();
      if (iVar2 == 0) {
        CExplosionInitThing__Helper_004beb30();
      }
      in_stack_00000024 = (void *)DAT_00809db4;
      in_stack_0000002c = (int *)DAT_00809db0;
      do {
        iVar4 = (int)in_stack_00000024;
        local_8 = CONCAT44(local_8._4_4_,in_stack_0000002c);
        iVar2 = (int)in_stack_0000002c * 2;
        _fStack00000014 = CONCAT44(fStack00000018,(int)in_stack_00000024 * 2 + 1);
        if (this[5] <= this[3]) {
          iVar1 = this[5] * 2;
          iVar3 = CPolyBucket__Helper_005491b0(this[4],iVar1);
          this[4] = iVar3;
          this[5] = iVar1;
          iVar1 = this[7];
          iVar3 = CPolyBucket__Helper_005491b0(this[6],iVar1 << 1);
          this[6] = iVar3;
          this[7] = iVar1 << 1;
        }
        *(char *)(this[4] + this[3]) = (char)((int)fStack00000014 >> 1);
        *(char *)(this[6] + this[3]) = (char)(iVar2 + 1 >> 1);
        this[3] = this[3] + 1;
        CExplosionInitThing__Unk_004bed30(&stack0x00000024,&stack0x0000002c);
        if ((in_stack_00000024 == (void *)iVar4) && (in_stack_0000002c == (int *)(uint)local_8)) {
          return (int)in_stack_00000024;
        }
      } while ((in_stack_00000024 != (void *)local_c) ||
              (in_stack_0000002c != (int *)fStack00000004));
      CExplosionInitThing__Unk_004beea0(this,(int)DAT_00809db8,unaff_EDI);
      this[2] = 1;
      iVar2 = extraout_EAX;
    }
  }
  return iVar2;
}
