pipeline {

	agent any

        triggers { cron('H 5 * * *') }

	parameters {
		string(name: 'BINARYNAME', defaultValue: 'makehuman-community', description: 'The name used in the output exe binary')
		choice(name: 'RELEASE', choices: ['False', 'True'], description: 'Is release build')
		string(name: 'VERSIONNAME', defaultValue: '1.2.0', description: 'Version part of file name (when release build)')
		string(name: 'DEPLOYDEST', defaultValue: 'joepal1976@ssh.tuxfamily.org:makehuman/makehuman-repository/nightly/', description: 'Where to copy final binary')
		booleanParam(name: 'ALLOWBRANCH', defaultValue: false, description: 'Check to allow building even when branch is not master')
	}

	stages {

		// Set up environment variables with filenames etc
		stage('configure') {
			steps {
				script {
					env.DISTDIR = "${env.WORKSPACE}/../dist"
					env.DATESTAMP = sh(
						script: "date +\"%Y%m%d\"",
						returnStdout: true
					).trim()
					env.EXPECTEDEXE = "${env.WORKSPACE}/../pynsist-work/build/nsis/makehuman-community_${env.DATESTAMP}.exe"
					env.EXENAME = "${params.BINARYNAME}-${env.DATESTAMP}-windows.exe"
					env.ZIPNAME = "${env.WORKSPACE}/../${params.BINARYNAME}-${env.DATESTAMP}-nightly-windows.zip"
					if (env.RELEASE == "True") {
						env.EXENAME = "${params.BINARYNAME}-${env.VERSIONNAME}-windows.exe"
						env.ZIPNAME = "${env.WORKSPACE}/../${params.BINARYNAME}-${env.VERSIONNAME}-windows.zip"
					}
					env.DESIREDEXE = "${env.DISTDIR}/${env.EXENAME}"
					env.PERFORMUPLOAD = true;

					sh "echo \"env.DISTDIR: ${env.DISTDIR}\""
					sh "echo \"env.DATESTAMP: ${env.DATESTAMP}\""
					sh "echo \"env.EXPECTEDEXE: ${env.EXPECTEDEXE}\""
					sh "echo \"env.EXENAME: ${env.EXENAME}\""
					sh "echo \"env.DESIREDEXE: ${env.DESIREDEXE}\""
					sh "echo \"env.ZIPNAME: ${env.ZIPNAME}\""
				}
			}
		}

		stage('failOnBranch') {
		    when {
		        not {
		            branch 'master'
		        }
		    }
		    steps
		    {
		        script {
                    if(!params.ALLOWBRANCH) {
                        error('Will not build branches automatically for now')
                    }
                }
		    }
		}

		// Create a pylint log file
		stage('pylint') {
			steps {
				script {
					dir("makehuman") {
						sh "python3 create_pylint_log.py"
					}
				}
			}
		}

		// Download asset binaries from github
		stage('downloadAssets') {
			steps {
				script {
					dir("makehuman") {
						sh "python3 download_assets_git.py"
					}
				}
			}
		}

		// Run asset compile scripts
		stage('compileAssets') {
			steps {
				dir("makehuman") {
					sh "python3 compile_models.py"
					sh "python3 compile_proxies.py"
					sh "python3 compile_targets.py"
				}
			}
		}

		// Create a build.conf with relevant settings
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

		// Clear away old checked out plugin directories
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

		// Remove traces of prior builds
		stage('cleanDist') {
			steps {
				script {
					sh "rm -f ${env.WORKSPACE}/../*.zip"
					sh "rm -rf ${env.DISTDIR}"
					sh "mkdir -p ${env.DISTDIR}"
				}
			}
		}

		// Clone plugins which are to be included in MH
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

		// Clone blender plugins which are to be bundled as zip files
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

		// Run the pynsist step for creating an NSIS installer
		stage('pynsist') {
			steps {
				dir("buildscripts/win32") {
					sh "python3 makePynsistBuild.py"
				}
			}
		}

		// Move the resulting EXE to the directory where we intend to collect the contents of the zip
		stage('moveBuildToDist') {
			steps {
				script {
					sh "mkdir -p ${env.DISTDIR}"
					sh "mkdir -p ${env.DISTDIR}/addons_for_blender_28x"
					sh "cp -v ${env.EXPECTEDEXE} ${env.DESIREDEXE}"
				}
			}
		}

		// Perform steps necessary to make MPFB installable as an addon in blender
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

		// Perform steps necessary to make MakeTarget installable as an addon in blender
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

		// Perform steps necessary to make MakeClothes installable as an addon in blender
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

		// Perform steps necessary to make MakeSkin installable as an addon in blender
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

		// Zip contents of destination folder into a release zip
		stage('buildDistZip') {
			steps {
				dir("${env.DISTDIR}") {
					script {
						sh "echo > README.txt \"Addons for blender 2.79 are not bundled. See the community homepage for these.\""
						sh "zip -r ${env.ZIPNAME} addons_for_blender_28x README.txt ${env.EXENAME}"
					}
				}
			}
		}

		stage('deleteOldNightly') {
			when {
				expression {
					params.RELEASE == "False"
				}

			}
			steps {
				script {
					sh "ssh joepal1976@ssh.tuxfamily.org 'rm ~/makehuman/makehuman-repository/nightly/makehuman-community-*-nightly-windows.zip'"
				}
			}
		}

		// Upload zip to destination
		stage('deploy') {
			steps {
				script {
					sh "scp ${env.ZIPNAME} ${params.DEPLOYDEST}"
				}
			}
		}
	}
}
