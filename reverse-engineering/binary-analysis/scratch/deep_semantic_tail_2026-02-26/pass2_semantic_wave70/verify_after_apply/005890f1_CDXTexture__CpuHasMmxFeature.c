/* address: 0x005890f1 */
/* name: CDXTexture__CpuHasMmxFeature */
/* signature: int __fastcall CDXTexture__CpuHasMmxFeature(int param_1, int param_2) */


/* WARNING: Removing unreachable block (ram,0x005890fd) */

int __fastcall CDXTexture__CpuHasMmxFeature(int param_1,int param_2)

{
  int iVar1;

  iVar1 = cpuid_Version_info(1);
  return (uint)((*(uint *)(iVar1 + 8) & 0x800000) != 0);
}
