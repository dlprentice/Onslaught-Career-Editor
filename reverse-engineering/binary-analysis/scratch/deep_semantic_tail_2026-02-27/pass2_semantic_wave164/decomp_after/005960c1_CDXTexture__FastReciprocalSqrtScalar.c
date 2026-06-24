/* address: 0x005960c1 */
/* name: CDXTexture__FastReciprocalSqrtScalar */
/* signature: double __stdcall CDXTexture__FastReciprocalSqrtScalar(uint param_1) */


double CDXTexture__FastReciprocalSqrtScalar(uint param_1)

{
  uint uVar1;

  uVar1 = param_1 >> 0xc & 0xff8;
  return (double)(((float)(param_1 & 0xffffff | 0x3f000000) * *(float *)(&DAT_00658c98 + uVar1) +
                  *(float *)(&DAT_00658c9c + uVar1)) *
                 (float)(0xbeffffff - param_1 >> 1 & 0xff800000));
}
