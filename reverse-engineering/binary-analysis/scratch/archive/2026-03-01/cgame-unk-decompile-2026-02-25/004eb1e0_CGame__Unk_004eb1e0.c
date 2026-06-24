/* address: 0x004eb1e0 */
/* name: CGame__Unk_004eb1e0 */
/* signature: void CGame__Unk_004eb1e0(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CGame__Unk_004eb1e0(void)

{
  float value;
  float local_c;

  D3DStateCache__ResetSentinelTable();
  if (DAT_00854e6c != '\0') {
    CEngine__SetVertexShadersEnabled(&DAT_00855bb0,'\0');
  }
  RenderState_SetRaw(0x1b,1);
  RenderState_SetRaw(0x13,5);
  RenderState_SetRaw(0x14,6);
  RenderState_SetRaw(0xf,1);
  RenderState_SetAlphaRefRaw(8);
  RenderState_SetRaw(0x19,7);
  RenderState_SetRaw(8,3);
  RenderState_SetRaw(0x16,3);
  RenderState_SetRaw(0xe,1);
  RenderState_SetRaw(7,1);
  RenderState_SetRaw(0x17,4);
  RenderState_SetRaw(0xa8,0xf);
  RenderState_SetRaw(0x34,0);
  RenderState_SetRaw(0x97,0);
  RenderState_SetRaw(0x1c,(uint)(DAT_0089d680 == '\0'));
  RenderState_SetRaw(0x1d,0);
  RenderState_Set_23_8C_Compat('\x01');
  RenderState_SetRaw(0x89,1);
  RenderState_SetRaw(0x1a,1);
  RenderState_SetRaw(9,2);
  RenderState_SetRaw(0x91,1);
  RenderState_SetRaw(0x92,0);
  RenderState_SetRaw(0x93,1);
  RenderState_SetRaw(0x94,0);
  RenderState_SetRaw(0x8f,0);
  RenderState_SetRaw(0x8b,-0xf330532);
  RenderState_SetRaw(0x22,-0xf330532);
  RenderState_SetRaw(0x26,-0xf330532);
  RenderState_SetRaw(0x24,-0xf330532);
  RenderState_SetRaw(0x25,-0xf330532);
  RenderState_SetRaw(0x3c,-0xf330532);
  RenderState_SetRaw(0x9c,0);
  RenderState_SetRaw(0x9d,0);
  if (_DAT_005d8568 < DAT_00888b04) {
    value = _DAT_005d8c44;
    if (DAT_00888b04 < _DAT_005d8c44) {
      value = DAT_00888b04;
    }
    if (_DAT_005db2b8 <= DAT_00888b04) {
      local_c = 32.0;
    }
    else {
      local_c = DAT_00888b04;
    }
    RenderState_SetRaw(0x9a,(int)value);
    RenderState_SetRaw(0x9b,(int)value);
    RenderState_SetRaw(0x9e,0);
    RenderState_SetRaw(0x9f,0);
    RenderState_SetRaw(0xa0,0x3f800000);
    RenderState_SetRaw(0xa6,(int)local_c);
  }
  RenderState_SetRaw(0x37,1);
  RenderState_SetRaw(0x34,0);
  RenderState_SetRaw(0x38,1);
  RenderState_SetRaw(0x39,0);
  CDXEngine__SetProjectionDepthBiasIndex(&DAT_009c65c0,0);
  RenderState_SetRaw(0x88,1);
  CUnit__Unk_004eba30(1);
  RenderState_SetRaw(0xa7,0);
  D3DStateCache__SetState114Cached(0,6,2);
  D3DStateCache__SetState114Cached(0,5,2);
  D3DStateCache__SetMipFilterLinear(0);
  D3DStateCache__SetState114Cached(0,10,1);
  D3DStateCache__SetState114Cached(0,1,1);
  D3DStateCache__SetState114Cached(0,2,1);
  D3DStateCache__SetStateRaw(0,2,2);
  D3DStateCache__SetStateRaw(0,3,0);
  D3DStateCache__SetStateRaw(0,5,2);
  D3DStateCache__SetStateRaw(0,6,0);
  D3DStateCache__SetStateRaw(0,1,4);
  D3DStateCache__SetStateRaw(0,4,4);
  D3DStateCache__SetStateRaw(0,0xb,0);
  D3DStateCache__SetStateRaw(0,0x18,0);
  D3DStateCache__SetState114Cached(0,8,0);
  D3DStateCache__SetState114Cached(0,4,0xffffffff);
  D3DStateCache__SetState114Cached(1,6,2);
  D3DStateCache__SetState114Cached(1,5,2);
  D3DStateCache__SetMipFilterByGlobalToggle(1);
  D3DStateCache__SetState114Cached(1,10,1);
  D3DStateCache__SetState114Cached(1,1,1);
  D3DStateCache__SetState114Cached(1,2,1);
  D3DStateCache__SetStateRaw(1,2,2);
  D3DStateCache__SetStateRaw(1,3,1);
  D3DStateCache__SetStateRaw(1,5,2);
  D3DStateCache__SetStateRaw(1,6,1);
  D3DStateCache__SetStateRaw(1,1,1);
  D3DStateCache__SetStateRaw(1,4,1);
  D3DStateCache__SetStateRaw(1,0xb,1);
  D3DStateCache__SetStateRaw(1,0x18,0);
  D3DStateCache__SetState114Cached(1,8,0);
  D3DStateCache__SetStateRaw(1,0x1a,3);
  D3DStateCache__SetState114Cached(1,4,0xffffffff);
  D3DStateCache__SetState114Cached(2,6,2);
  D3DStateCache__SetState114Cached(2,5,2);
  D3DStateCache__SetMipFilterByGlobalToggle(2);
  D3DStateCache__SetState114Cached(2,10,1);
  D3DStateCache__SetState114Cached(2,1,1);
  D3DStateCache__SetState114Cached(2,2,1);
  D3DStateCache__SetStateRaw(2,2,2);
  D3DStateCache__SetStateRaw(2,3,1);
  D3DStateCache__SetStateRaw(2,5,2);
  D3DStateCache__SetStateRaw(2,6,1);
  D3DStateCache__SetStateRaw(2,1,1);
  D3DStateCache__SetStateRaw(2,4,1);
  D3DStateCache__SetStateRaw(2,0xb,2);
  D3DStateCache__SetStateRaw(2,0x18,0);
  D3DStateCache__SetState114Cached(2,8,0);
  D3DStateCache__SetStateRaw(2,0x1a,3);
  D3DStateCache__SetState114Cached(2,4,0xffffffff);
  D3DStateCache__SetState114Cached(3,6,2);
  D3DStateCache__SetState114Cached(3,5,2);
  D3DStateCache__SetMipFilterByGlobalToggle(3);
  D3DStateCache__SetState114Cached(3,10,1);
  D3DStateCache__SetState114Cached(3,1,1);
  D3DStateCache__SetState114Cached(3,2,1);
  D3DStateCache__SetStateRaw(3,2,2);
  D3DStateCache__SetStateRaw(3,3,1);
  D3DStateCache__SetStateRaw(3,5,2);
  D3DStateCache__SetStateRaw(3,6,1);
  D3DStateCache__SetStateRaw(3,1,1);
  D3DStateCache__SetStateRaw(3,4,1);
  D3DStateCache__SetStateRaw(3,0xb,3);
  D3DStateCache__SetStateRaw(3,0x18,0);
  D3DStateCache__SetState114Cached(3,8,0);
  D3DStateCache__SetStateRaw(3,0x1a,3);
  D3DStateCache__SetState114Cached(3,4,0xffffffff);
  return;
}
