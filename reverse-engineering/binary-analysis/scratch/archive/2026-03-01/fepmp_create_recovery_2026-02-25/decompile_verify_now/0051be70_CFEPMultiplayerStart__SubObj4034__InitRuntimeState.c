/* address: 0x0051be70 */
/* name: CFEPMultiplayerStart__SubObj4034__InitRuntimeState */
/* signature: void __fastcall CFEPMultiplayerStart__SubObj4034__InitRuntimeState(void * this) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CFEPMultiplayerStart__SubObj4034__InitRuntimeState(void *this)

{
  int unaff_ESI;
  float fVar1;

  fVar1 = PLATFORM__GetSysTimeFloat();
  *(float *)((int)this + 4) = fVar1;
  _DAT_0089d9cc = 0xffffffff;
  CVBufTexture__Unk_00527960(&DAT_0089be50,0,unaff_ESI);
  CVBufTexture__Unk_00527960(&DAT_0089be5c,0,unaff_ESI);
  *(undefined4 *)((int)this + 0x18) = 0;
  return;
}
