/* address: 0x0058f331 */
/* name: CTexture__ReleaseSymbolHashTables */
/* signature: void __fastcall CTexture__ReleaseSymbolHashTables(int param_1) */


void __fastcall CTexture__ReleaseSymbolHashTables(int param_1)

{
  CDXTexture__ReleaseTexturePointerArray7(param_1 + 0x38);
  CDXTexture__ReleaseTexturePointerArray7(param_1 + 0x1c);
  CDXTexture__ReleaseTexturePointerArray7(param_1);
  return;
}
