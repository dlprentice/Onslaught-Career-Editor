/* address: 0x0056b2b3 */
/* name: CDXTexture__Helper_0056b2b3 */
/* signature: void __cdecl CDXTexture__Helper_0056b2b3(uint param_1) */


void __cdecl CDXTexture__Helper_0056b2b3(uint param_1)

{
  LeaveCriticalSection
            ((LPCRITICAL_SECTION)
             ((&DAT_009d32a0)[(int)param_1 >> 5] + 0xc + (param_1 & 0x1f) * 0x24));
  return;
}
