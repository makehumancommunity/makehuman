pipeline {
    
    agent any
    
    parameters {
        string(name: 'BINARYNAME', defaultValue: 'makehuman-community', description: 'The name used in the output exe binary')
        choice(name: 'RELEASE', choices: ['False', 'True'], description: 'Is release build')
        string(name: 'DEPLOYDEST', defaultValue: 'joepal1976@ssh.tuxfamily.org:makehuman/makehuman-repository/nightly/', description: 'Where to copy final binary')
    }

    stages {
        stage('configure') {
            steps {
                script {
                    env.DISTDIR = "${env.WORKSPACE}/../dist"
                    env.DATESTAMP = sh(
                        script: "date +\"%Y%m%d\"",
                        returnStdout: true
                    ).trim()
                    env.EXPECTEDEXE = "${env.WORKSPACE}/../pynsist-work/build/nsis/makehuman-community_${env.DATESTAMP}.exe"
                    env.DESIREDEXE = "${env.DISTDIR}/${params.BINARYNAME}-${env.DATESTAMP}-win32.exe"
                
                    sh "echo \"env.DISTDIR: ${env.DISTDIR}\""
                    sh "echo \"env.DATESTAMP: ${env.DATESTAMP}\""
                    sh "echo \"env.EXPECTEDEXE: ${env.EXPECTEDEXE}\""
                    sh "echo \"env.DESIREDEXE: ${env.DESIREDEXE}\""
                }
            }
        }

      //stage('scm') {
      //   steps {
      //      git 'https://github.com/makehumancommunity/makehuman'
      //   }
      //}

      stage('downloadAssets') {
        steps {
            script {
                dir("makehuman") {
                    sh "python3 download_assets_git.py"
                }
            }
        }
      }

      stage('compileAssets') {
        steps {
            dir("makehuman") {
                sh "python3 compile_models.py"
                sh "python3 compile_proxies.py"
                sh "python3 compile_targets.py"
            }
        }
      }

      stage('createBuildConf') {
          steps {
              dir("buildscripts") {
                  sh "echo -n > build.conf"
                  sh "echo >> build.conf \"[General]\n\n[BuildPrepare]\n\""
                  sh "echo >> build.conf \"isRelease = ${params.RELEASE}\""
                  sh "echo >> build.conf \"noDownload = True\""
                  sh "echo >> build.conf \"skipScripts = True\n\""
                  sh "echo >> build.conf \"[Deb]\n\n[Rpm]\n\""
                  sh "echo >> build.conf \"[Win32]\""
                  sh "echo >> build.conf \"packageName = makehumancommunity\""
                  sh "echo >> build.conf \"distDir = ${env.WORKSPACE}/dist\""
              }
          }
      }

    stage('cleanPlugins') {
          steps {
              
                  script {
                    sh "rm -rf ${env.WORKSPACE}/../mhx2-makehuman-exchange"      
                    sh "rm -rf ${env.WORKSPACE}/../community-plugins-assetdownload"      
                    sh "rm -rf ${env.WORKSPACE}/../community-plugins-mhapi"      
                    sh "rm -rf ${env.WORKSPACE}/../community-plugins-socket"      
                    sh "rm -rf ${env.WORKSPACE}/../community-plugins-massproduce"
                    sh "rm -rf ${env.WORKSPACE}/../community-plugins-makeclothes"      
                    sh "rm -rf ${env.WORKSPACE}/../community-plugins-makeskin"      
                    sh "rm -rf ${env.WORKSPACE}/../community-plugins-maketarget"      
                    sh "rm -rf ${env.WORKSPACE}/../makehuman-plugin-for-blender"      
                  }
              
          }
      }

      stage('cloneMHPlugins') {
          steps {
              script {
                  sh "pwd"
                    sh "git clone https://github.com/makehumancommunity/mhx2-makehuman-exchange ${env.WORKSPACE}/../mhx2-makehuman-exchange"      
                    sh "git clone https://github.com/makehumancommunity/community-plugins-assetdownload ${env.WORKSPACE}/../community-plugins-assetdownload"      
                    sh "git clone https://github.com/makehumancommunity/community-plugins-mhapi ${env.WORKSPACE}/../community-plugins-mhapi"      
                    sh "git clone https://github.com/makehumancommunity/community-plugins-socket ${env.WORKSPACE}/../community-plugins-socket"      
                    sh "git clone https://github.com/makehumancommunity/community-plugins-massproduce ${env.WORKSPACE}/../community-plugins-massproduce"
              }
              
          }
      }

      stage('cloneBlenderPlugins') {
          steps {
              script {
                  
                    sh "git clone https://github.com/makehumancommunity/makehuman-plugin-for-blender ${env.WORKSPACE}/../makehuman-plugin-for-blender"      
                    sh "git clone https://github.com/makehumancommunity/community-plugins-makeclothes ${env.WORKSPACE}/../community-plugins-makeclothes"      
                    sh "git clone https://github.com/makehumancommunity/community-plugins-maketarget ${env.WORKSPACE}/../community-plugins-maketarget"      
                    sh "git clone https://github.com/makehumancommunity/community-plugins-makeskin ${env.WORKSPACE}/../community-plugins-makeskin"      
                    sh "ls -l ${env.WORKSPACE}/.."
              }
          
          }
      }

      stage('pynsist') {
          steps {
              dir("buildscripts/win32") {
                  sh "python3 makePynsistBuild.py"
              }
          }
      }

      stage('moveBuildToDist') {
          steps {
              script {
                  sh "mkdir -p ${env.DISTDIR}"
                  sh "mkdir -p ${env.DISTDIR}/addons_for_blender_28x"
                  sh "cp -v ${env.EXPECTEDEXE} ${env.DESIREDEXE}"
              }
          }
      }

      stage('blenderizeMPFB') {
          steps {
              dir("${env.WORKSPACE}/../makehuman-plugin-for-blender/blender_source") {
                  script {
                      sh "echo > README.txt \"Do not extract this file. It should be installed as an addon zip in blender.\""
                      sh "zip -r ${env.DISTDIR}/addons_for_blender_28x/makehuman-plugin-for-blender.zip MH_Community README.txt"
                  }
              }
          }
      }

      stage('blenderizeMakeTarget') {
          steps {
              dir("${env.WORKSPACE}/../community-plugins-maketarget") {
                  script {
                      sh "echo > README.txt \"Do not extract this file. It should be installed as an addon zip in blender.\""
                      sh "zip -r ${env.DISTDIR}/addons_for_blender_28x/maketarget2.zip maketarget README.txt"
                  }
              }
          }
      }

      stage('blenderizeMakeClothes') {
          steps {
              dir("${env.WORKSPACE}/../community-plugins-makeclothes") {
                  script {
                      sh "echo > README.txt \"Do not extract this file. It should be installed as an addon zip in blender.\""
                      sh "zip -r ${env.DISTDIR}/addons_for_blender_28x/makeclothes2.zip makeclothes README.txt"
                  }
              }
          }
      }

      stage('blenderizeMakeSkin') {
          steps {
              dir("${env.WORKSPACE}/../community-plugins-makeskin") {
                  script {
                      sh "echo > README.txt \"Do not extract this file. It should be installed as an addon zip in blender.\""
                      sh "zip -r ${env.DISTDIR}/addons_for_blender_28x/makeskin.zip makeskin README.txt"
                  }
              }
          }
      }

      stage('buildDistZip') {
          steps {
              dir("${env.DISTDIR}") {
                  script {
                      sh "echo > README.txt \"Addons for blender 2.79 are not bundled. See the community homepage for these.\""
                      sh "zip -r ${env.WORKSPACE}/${params.BINARYNAME}-${env.DATESTAMP}-win32.zip addons_for_blender_28x README.txt ${params.BINARYNAME}-${env.DATESTAMP}-win32.exe"
                  }
              }
          }
      }

      stage('deploy') {
          steps {
              script {
                  sh "scp ${env.WORKSPACE}/${params.BINARYNAME}-${env.DATESTAMP}-win32.zip ${params.DEPLOYDEST}"
              }
          }
      }
   }
}
