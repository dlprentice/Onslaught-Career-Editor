/* address: 0x00482210 */
/* name: CUnitAI__Helper_00482210 */
/* signature: int CUnitAI__Helper_00482210(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CUnitAI__Helper_00482210(void)

{
  float fVar1;
  float fVar2;
  undefined2 extraout_var;
  undefined2 extraout_var_00;
  undefined2 extraout_var_01;
  undefined2 uVar4;
  int iVar3;
  int extraout_EAX;
  int extraout_EAX_00;
  int in_ECX;
  float p9;
  float in_stack_00000004;
  float in_stack_00000008;
  float in_stack_0000000c;
  float in_stack_00000010;
  float in_stack_00000014;
  int local_8;

  RenderState_Set(0x13,5);
  RenderState_Set(0x14,6);
  CDXEngine__ApplyPendingRenderState(&DAT_009c65c0,'\0');
  if (in_stack_00000010 < _DAT_005d85cc) {
    in_stack_00000010 = 10.0;
  }
  if (in_stack_00000014 == _DAT_005d8568) {
    fVar2 = in_stack_00000010 * _DAT_005dbb4c;
    fVar1 = in_stack_0000000c * _DAT_005d85ec;
    in_stack_00000014 = in_stack_00000004 - fVar1;
    CVBufTexture__DrawSpriteEx
              (in_stack_00000014,in_stack_00000008,0.009,*(void **)(in_ECX + 0x154),4,0,1.0,0.0,-NAN
               ,fVar2,fVar2,0.0,1.0,0.0,1.0);
    CVBufTexture__DrawSpriteEx
              (in_stack_00000014,in_stack_00000008,0.009,*(void **)(in_ECX + 0x15c),7,0,1.0,0.0,
               -2.524355e-29,fVar2,fVar2,0.0,1.0,0.0,1.0);
    fVar1 = fVar1 + in_stack_00000004;
    CVBufTexture__DrawSpriteEx
              (fVar1,in_stack_00000008,0.009,*(void **)(in_ECX + 0x158),4,0,1.0,0.0,-NAN,fVar2,fVar2
               ,0.0,1.0,0.0,1.0);
    CVBufTexture__DrawSpriteEx
              (fVar1,in_stack_00000008,0.009,*(void **)(in_ECX + 0x164),8,0,1.0,0.0,-2.524355e-29,
               fVar2,fVar2,0.0,1.0,0.0,1.0);
    fVar1 = fVar2 * _DAT_005dbb64;
    in_stack_00000010 = in_stack_0000000c / fVar1;
    uVar4 = extraout_var_00;
    if (_DAT_005d8568 <= in_stack_00000010) {
      do {
        CVBufTexture__DrawSpriteEx
                  (in_stack_00000014,in_stack_00000008,0.009,*(void **)(in_ECX + 0x160),8,0,1.0,0.0,
                   -2.524355e-29,fVar2,fVar2,0.0,1.0,0.0,1.0);
        in_stack_00000010 = in_stack_00000010 - _DAT_005d8568;
        in_stack_00000014 = fVar1 + in_stack_00000014;
        uVar4 = extraout_var_01;
      } while (_DAT_005d8568 <= in_stack_00000010);
    }
    iVar3 = CONCAT22(uVar4,(ushort)(in_stack_00000010 < _DAT_005d856c) << 8 |
                           (ushort)(NAN(in_stack_00000010) || NAN(_DAT_005d856c)) << 10 |
                           (ushort)(in_stack_00000010 == _DAT_005d856c) << 0xe);
    if (in_stack_00000010 >= _DAT_005d856c && (in_stack_00000010 == _DAT_005d856c) == 0) {
      CVBufTexture__DrawSpriteEx
                (in_stack_00000014,in_stack_00000008,0.009,*(void **)(in_ECX + 0x160),8,1,
                 in_stack_00000010,0.0,-2.524355e-29,fVar2,fVar2,0.0,1.0,0.0,1.0);
      return extraout_EAX;
    }
  }
  else {
    iVar3 = CONCAT22(extraout_var,
                     (ushort)(in_stack_00000014 < _DAT_005d85ec) << 8 |
                     (ushort)(NAN(in_stack_00000014) || NAN(_DAT_005d85ec)) << 10 |
                     (ushort)(in_stack_00000014 == _DAT_005d85ec) << 0xe);
    if (in_stack_00000014 >= _DAT_005d85ec && (in_stack_00000014 == _DAT_005d85ec) == 0) {
      iVar3 = CONCAT22(extraout_var,
                       (ushort)(in_stack_00000014 < _DAT_005d8568) << 8 |
                       (ushort)(NAN(in_stack_00000014) || NAN(_DAT_005d8568)) << 10 |
                       (ushort)(in_stack_00000014 == _DAT_005d8568) << 0xe);
      if (in_stack_00000014 < _DAT_005d8568) {
        fVar1 = in_stack_00000010 * in_stack_00000014 * _DAT_005dbb4c;
        local_8 = (int)(longlong)ROUND(in_stack_00000014 * _DAT_005d8c70);
        if (local_8 < 0) {
          local_8 = 0;
        }
        else if (0xff < local_8) {
          local_8 = 0xff;
        }
        fVar2 = _DAT_005d8568 - in_stack_00000014;
        p9 = (float)(local_8 * 0xff0000 | 0xffffff);
        CVBufTexture__DrawSpriteEx
                  (in_stack_00000004,in_stack_00000008,0.009,*(void **)(in_ECX + 0x154),4,0,1.0,
                   fVar2,p9,fVar1,fVar1,0.0,1.0,0.0,1.0);
        CVBufTexture__DrawSpriteEx
                  (in_stack_00000004,in_stack_00000008,0.009,*(void **)(in_ECX + 0x158),4,0,1.0,
                   fVar2,p9,fVar1,fVar1,0.0,1.0,0.0,1.0);
        iVar3 = extraout_EAX_00;
      }
    }
  }
  return iVar3;
}
